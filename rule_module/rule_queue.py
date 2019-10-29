import json
from project.models import Project
from django.core.exceptions import ObjectDoesNotExist
from final_fusion.models import FinalFusion
from final_fusion_column.models import FinalFusionColumn
from rule_module.models import RuleModule
from script_module.models import ScriptModule

# Condition names
APPLY = "APPLY"
REPLACE = "REPLACE"
IGNORE = "IGNORE"
CONTAINS = "CONTAINS"


class RuleQueue:
    """
    RuleQueue
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
        add_all_rule_modules
        """
        ff = FinalFusion.objects.get(project=Project.objects.get(pk=user_profile.last_opened_project_id))
        self.rule_modules = list(RuleModule.objects.filter(final_fusion=ff, archived=False).order_by("pk"))
        self.script_modules = ScriptModule.objects.filter(final_fusion=ff, archived=False).order_by("pk")

    def replace_content(self, orig, haystack, needle):
        """
        replace_content
        """
        self.applied_count += 1

        if self.changes_visible:
            needle = self.span_tag % needle

        if "span" in orig:
            content = orig.replace("<span class='ruled'>", "").replace("</span>", "")
            haystack = haystack.replace("<span class='ruled'>", "").replace("</span>", "")
            c_needle = needle.replace("<span class='ruled'>", "").replace("</span>", "")

            # Check if really something to replace, maybe it was a char from the tags
            if haystack in content:
                combined = "%s, %s" % (content, c_needle)
                return self.span_tag % combined
        elif len(orig) > 1 and len(needle) > 1:
            orig = "%s, %s" % (orig, needle)
        else:
            orig = orig.replace(haystack, needle)

        return orig

    def apply(self):
        """
        apply
        """
        for sm in self.script_modules:
            for row in self.table["out_rows"]:
                sm.apply_to_row(row, self.span_tag, self.changes_visible)

        for rm in self.rule_modules:
            if_condition = json.loads(rm.if_conditions)
            then_cases = json.loads(rm.then_cases)

            if rm.rule_type == "col":
                self.apply_col_rms(rm, if_condition, then_cases)

            elif rm.rule_type == "row":
                self.apply_row_rms(if_condition, then_cases)

    def apply_col_rms(self, rm, if_cond, then_cases):
        """
        apply_col_rms
        """
        subject_name = FinalFusionColumn.objects.get(pk=json.loads(rm.col_subject)[0]).get_as_json()["name"]

        for row in self.table["out_rows"]:
            if subject_name in row:
                if "when_contains" in if_cond:
                    if "then_apply" in then_cases:
                        if if_cond["when_contains"] in row[subject_name]:
                            row[subject_name] = self.span_tag % then_cases["then_apply"]
                    elif "then_replace" in then_cases:
                        # Important to check if already in span
                        if if_cond["when_contains"] in row[subject_name]:
                            row[subject_name] = self.replace_content(row[subject_name], if_cond["when_contains"],
                                                                     then_cases["then_replace"])

                if "when_is" in if_cond and "then_apply" in then_cases:
                    if row[subject_name] == if_cond["when_is"]:
                        row[subject_name] = self.replace_content(row[subject_name], if_cond["when_is"],
                                                                 then_cases["then_apply"])

    def apply_row_rms(self, if_condition, then_cases):
        """
        apply_row_rms
        """
        for row in self.table["out_rows"]:
            trimmed_col_names = [{"short": c.split("(")[0].strip(), "long": c} for c in list(row.keys())]

            for and_bracket in if_condition:
                # All of the values in the list have to be true
                bool_vals = [False for i in and_bracket]

                for ic in and_bracket:
                    # Now check if there's something which could apply
                    for tcn in trimmed_col_names:
                        if ic["ffc_name"] == tcn["short"]:
                            col_val = row[tcn["long"]]
                            if ic["condition"] == "IS" and str(col_val) == ic["value"] \
                                    or ic["condition"] == CONTAINS and ic["value"] in str(col_val):
                                bool_vals[and_bracket.index(ic)] = True
                                break

                if all(bool_vals):
                    # Alle then cases übernehmen
                    for tc in then_cases:
                        try:
                            ffc = FinalFusionColumn.objects.get(pk=tc["id"]).get_as_json()
                        except ObjectDoesNotExist:
                            ffc = None

                        if tc["action"] == IGNORE:
                            if self.changes_visible:
                                row["__ignore"] = True
                            else:
                                del self.table["out_rows"][self.table["out_rows"].index(row)]
                        else:
                            if tc["action"] == APPLY:
                                if tc["ffc_name"] in row:
                                    row[tc["ffc_name"]] = self.replace_content(row[tc["ffc_name"]],
                                                                               row[tc["ffc_name"]], tc["value"])
                                elif ffc["name"] in row:
                                    # For cols with (source) in name
                                    row[ffc["name"]] = self.replace_content(row[ffc["name"]], row[ffc["name"]],
                                                                            tc["value"])

                            elif tc["action"] == REPLACE:
                                if tc["ffc_name"] in row:
                                    row[tc["ffc_name"]] = self.replace_content(row[tc["ffc_name"]], tc["value"],
                                                                               tc["value_replace"])
                                elif ffc["name"] in row:
                                    row[ffc["name"]] = self.replace_content(row[ffc["name"]], tc["value"],
                                                                            tc["value_replace"])
