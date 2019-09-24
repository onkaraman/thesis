import json
from user_profile.models import UserProfile
from project.models import Project
from final_fusion.models import FinalFusion
from final_fusion_column.models import FinalFusionColumn
from rule_module.models import RuleModule


class RuleQueue:
    """
    RuleQueue
    """

    def __init__(self, table):
        self.table = table
        self.rule_modules = []
        self.span_tag = "<span class='ruled'>%s</span>"

    def add_all_user_rule_modules(self, user_profile):
        """
        add_all_user_rule_modules
        """
        ff = FinalFusion.objects.get(project=Project.objects.get(pk=user_profile.last_opened_project_id))
        self.rule_modules = list(RuleModule.objects.filter(final_fusion=ff, archived=False))

    def replace_in_span(self, span, haystack, needle):
        """
        replace_in_span
        """
        content = span.replace("<span class='ruled'>", "").replace("</span>", "")
        # Check if really something to replace, maybe it was a char from the tags
        if haystack in content:
            return self.span_tag % content.replace(haystack, needle)
        else:
            return span

    def apply(self):
        """
        apply
        """
        for rm in self.rule_modules:
            if_condition = json.loads(rm.if_conditions)
            then_cases = json.loads(rm.then_cases)

            if rm.rule_type == "col":
                subject_name = FinalFusionColumn.objects.get(pk=json.loads(rm.col_subject)[0]).get_as_json()["name"]

                for row in self.table["out_rows"]:
                    if subject_name in row:
                        if "when_contains" in if_condition:
                            if "then_apply" in then_cases:
                                if if_condition["when_contains"] in row[subject_name]:
                                    row[subject_name] = self.span_tag % then_cases["then_apply"]
                            elif "then_replace" in then_cases:
                                # Important to check if already in span
                                if if_condition["when_contains"] in row[subject_name]:
                                    if "span" in row[subject_name]:
                                        row[subject_name] = self.replace_in_span(row[subject_name],
                                                                                 if_condition["when_contains"],
                                                                                 then_cases["then_replace"])
                                    else:
                                        row[subject_name] = row[subject_name].replace(if_condition["when_contains"],
                                                                                      self.span_tag
                                                                                      % then_cases["then_replace"])
                        if "when_is" in if_condition and "then_apply" in then_cases:
                            if row[subject_name] == if_condition["when_is"]:
                                row[subject_name] = self.span_tag % then_cases["then_apply"]

            elif rm.rule_type == "row":
                for row in self.table["out_rows"]:
                    trimmed_col_names = [{"short": c.split("(")[0].strip(), "long": c} for c in list(row.keys())]
                    can_apply_then = False

                    for and_bracket in if_condition:
                        for ic in and_bracket:

                            # Now check if there's something which could apply
                            for tcn in trimmed_col_names:
                                if ic["ffc_name"] == tcn["short"]:
                                    col_val = row[tcn["long"]]
                                    if ic["condition"] == "IS" and col_val == ic["value"] \
                                            or ic["condition"] == "CONTAINS" and ic["value"] in col_val:
                                        can_apply_then = True
                        if can_apply_then:
                            # Alle then cases übernehmen
                            for tc in then_cases:
                                for tcn in trimmed_col_names:
                                    if tc["ffc_name"] == tcn["short"]:
                                        if tc["action"] == "APPLY":
                                            row[tcn["long"]] = self.span_tag % tc["value"]
                                        elif tc["action"] == "REPLACE":
                                            row[tcn["long"]] = row[tcn["long"]].replace(tc["value"],
                                                                                         self.span_tag %
                                                                                         tc["value_replace"])
