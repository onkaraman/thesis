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
        rms = RuleModule.objects.filter(final_fusion=ff)
        for rm in rms:
            self.rule_modules.append(rm)

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
                subject_name = FinalFusionColumn.objects.get(pk=json.loads(rm.subjects)[0]).get_as_json()["name"]

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
