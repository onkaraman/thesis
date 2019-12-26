import json
from project.models import Project
from django.core.exceptions import ObjectDoesNotExist
from final_fusion.models import FinalFusion
from final_fusion_column.models import FinalFusionColumn
from rule_module.models import RuleModule
from script_module.models import ScriptModule

# Condition names
APPLY = "APPLY"
ATTACH = "ATTACH"
REPLACE = "REPLACE"
IGNORE = "IGNORE"
CONTAINS = "CONTAINS"


class RuleQueue:
    """
    A rule queue applies all rules of a TF/FF by queing the first rm to the last rm.
    """
    def __init__(self, table, changes_visible=True):
        self.table = table
        self.rule_modules = []
        self.script_modules = []
        self.span_tag = "<span class='ruled'>%s</span>"
        self.changes_visible = changes_visible
        self.applied_count = 0

    def add_all_rule_modules(self, user_profile):
        """
        Will add all rule modules to the queue.
        """
        ff = FinalFusion.objects.get(project=Project.objects.get(pk=user_profile.last_opened_project_id))
        self.rule_modules = list(RuleModule.objects.filter(final_fusion=ff, archived=False).order_by("pk"))
        self.script_modules = ScriptModule.objects.filter(final_fusion=ff, archived=False).order_by("pk")

    def replace_content(self, orig, haystack, needle, append=False):
        """
        Will replace the original cell content with the one, which results after the rule applied.
        :param orig: Original cell value (might be replaced content already).
        :param haystack: What to look for in replace-cases.
        :param needle: What to replace from the haystack.
        :param append: When True, the post-rm content will be appended to the cell content.
        """
        orig = str(orig)
        haystack = str(haystack)
        needle = str(needle)

        self.applied_count += 1

        if self.changes_visible:
            needle = self.span_tag % needle

        # Already modified cell.

        if "span" in orig:
            content = orig.replace("<span class='ruled'>", "").replace("</span>", "")
            haystack = haystack.replace("<span class='ruled'>", "").replace("</span>", "")
            c_needle = needle.replace("<span class='ruled'>", "").replace("</span>", "")

            # Check if really something to replace, maybe it was a char from the tags
            if haystack in content:
                if append:
                    combined = "%s, %s" % (content, c_needle)
                else:
                    combined = "%s" % c_needle
                return self.span_tag % combined

        elif len(orig) > 1 and len(needle) > 1 and append:
            orig = "%s, %s" % (orig, needle)
        else:
            orig = orig.replace(haystack, needle)

        return orig

    def apply(self, export=False):
        """
        Will apply all rules modules to the TF/EF rows. Will apply scripts first.
        """
        for rm in self.rule_modules:
            if_condition = json.loads(rm.if_conditions)
            then_cases = json.loads(rm.then_cases)

            if rm.rule_type == "col":
                self.apply_col_rms(rm, if_condition, then_cases)

            elif rm.rule_type == "row":
                self.apply_row_rms(if_condition, then_cases)

        for sm in self.script_modules:
            for row in self.table["out_rows"]:
                # Modify row by script-rm.
                sm.apply_to_row(row, self.span_tag, self.changes_visible)

        if export:
            # If export, remove the .SUM and .AVG entries of each row.
            out_rows = []
            for r in self.table["out_rows"]:
                d = {}
                for k in r.keys():
                    if ".SUM" not in k and ".AVG" not in k:
                        d[k] = r[k]
                out_rows.append(d)
            self.table["out_rows"] = out_rows

    def apply_col_rms(self, rm, if_cond, then_cases):
        """
        Will apply column-rule modules. Will extract the stored if-conditions and then-cases
        and follow instructions.
        """
        subject_name = FinalFusionColumn.objects.get(pk=json.loads(rm.col_subject)[0]).get_as_json()["name"]

        for row in self.table["out_rows"]:
            if subject_name in row:
                if "when_contains" in if_cond:
                    if "then_apply" in then_cases:
                        if if_cond["when_contains"] in str(row[subject_name]):
                            row[subject_name] = self.span_tag % then_cases["then_apply"]
                    elif "then_replace" in then_cases:
                        # Important to check if already in span
                        if if_cond["when_contains"] in str(row[subject_name]):
                            row[subject_name] = self.replace_content(str(row[subject_name]), if_cond["when_contains"],
                                                                     then_cases["then_replace"])

                if "when_is" in if_cond and "then_apply" in then_cases:
                    if row[subject_name] == if_cond["when_is"]:
                        row[subject_name] = self.replace_content(row[subject_name], if_cond["when_is"],
                                                                 then_cases["then_apply"])

    def apply_row_rms(self, if_condition, then_cases):
        """
        Will apply a row-rule module. For each row, it will first check whether every condition of a single
        and-bracket is True. If so, it will apply the then-instructions of the RM to the current row.
        """
        for row in self.table["out_rows"]:
            # Create dict to map non-brackets names with original
            col_name_map = {}
            for n in row:
                col_name_map[n.split("(")[0].strip()] = n

            for and_bracket in if_condition:
                # All of the values in the list have to be true
                bool_vals = [False for i in and_bracket]

                for if_cond in and_bracket:
                    # Now check if there's something which could apply
                    for n in col_name_map:
                        if if_cond["ffc_name"] == n:
                            col_val = row[col_name_map[n]]
                            if if_cond["condition"] == "IS" and str(col_val) == if_cond["value"] \
                                    or if_cond["condition"] == CONTAINS and if_cond["value"] in str(col_val):
                                bool_vals[and_bracket.index(if_cond)] = True
                                break

                if all(bool_vals):
                    # Now apply all then-cases.
                    for tc in then_cases:
                        # Only dynamic cols have -1 as IDs.

                        try:
                            ffc = FinalFusionColumn.objects.get(pk=tc["id"]).get_as_json()
                        except ObjectDoesNotExist:
                            ffc = None

                        if tc["action"] == IGNORE:
                            if self.changes_visible:
                                # This entry will be used in the UI to indicate that the row is to be ignored.
                                row["__ignore"] = True
                            else:
                                # Remove this row for the export.
                                del self.table["out_rows"][self.table["out_rows"].index(row)]
                        else:
                            if tc["action"] == APPLY or tc["action"] == ATTACH:
                                if tc["ffc_name"] in col_name_map:
                                    mapped = row[col_name_map[tc["ffc_name"]]]
                                    row[col_name_map[tc["ffc_name"]]] = self.replace_content(mapped, mapped,
                                                                                             tc["value"],
                                                                                             append=tc["action"]==ATTACH)

                            elif tc["action"] == REPLACE:
                                if tc["ffc_name"] in col_name_map:
                                    mapped = row[col_name_map[tc["ffc_name"]]]
                                    row[col_name_map[tc["ffc_name"]]] = self.replace_content(mapped,
                                                                                         tc["value"],
                                                                                         tc["value_replace"])

