import json
from django.http import HttpResponse
from security.args_checker import ArgsChecker
import security.token_checker as token_checker
from django.core.exceptions import ObjectDoesNotExist
from final_fusion.models import FinalFusion
from final_fusion_column.models import FinalFusionColumn
from rule_module.models import RuleModule
from project.models import Project


def convert_request_bool_values(get_params):
    d = {}
    for key in get_params.keys():
        if get_params[key] == "true":
            d[key] = True
        elif get_params[key] == "false":
            d[key] = False
        else:
            d[key] = get_params[key]
    return d


def rule_condition_check(request):
    """
    rule_condition_check
    """
    if "when_is" in request.GET and "when_contains" in request.GET \
            and "when_value" in request.GET and not ArgsChecker.str_is_malicious(request.GET["when_value"]) \
            and "then_apply" in request.GET and "then_replace" in request.GET \
            and "then_value" in request.GET and not ArgsChecker.str_is_malicious(request.GET["then_value"]) \
            and "subject_id" in request.GET and ArgsChecker.is_number(request.GET["subject_id"]):
        return True
    return False


def request_to_rm(request, id=None):
    """
    request_to_rm
    """
    get_params = convert_request_bool_values(request.GET)

    subject_id = get_params["subject_id"]
    when_is = get_params["when_is"]
    when_contains = get_params["when_contains"]
    when_value = get_params["when_value"]
    then_apply = get_params["then_apply"]
    then_replace = get_params["then_replace"]
    then_value = get_params["then_value"]

    rm = RuleModule()
    if id:
        rm = RuleModule.objects.get(pk=id)
        subject_id = json.loads(rm.subjects)[0]

    if len(when_value) > 0 and len(then_value) > 0:
        try:
            ffc = FinalFusionColumn.objects.get(pk=subject_id)
            rm.rule_type = "col"
            rm.subjects = json.dumps([ffc.pk])

            if ((when_is and not when_contains) or (not when_is and when_contains)) \
                    and ((then_apply and not then_replace) or (not then_apply and then_replace)):

                # Construct if condition
                if_condition = {}
                if when_is:
                    if_condition["when_is"] = when_value
                elif when_contains:
                    if_condition["when_contains"] = when_value

                # Construct then
                then_case = {}
                if then_apply:
                    then_case["then_apply"] = then_value
                elif then_replace:
                    then_case["then_replace"] = then_value

                rm.if_conditions = json.dumps(if_condition)
                rm.then_cases = json.dumps(then_case)
                rm.final_fusion = ffc.final_fusion
                rm.name = "When %s, then %s" % (when_value, then_value)
                return rm

        except ObjectDoesNotExist:
            return None


def do_create_col_rm(request):
    """
    do_create_col_rm
    """
    success = False
    valid_user = token_checker.token_is_valid(request)
    if valid_user and rule_condition_check(request):
        rm = request_to_rm(request)
        rm.save()
        if rm:
            success = True

    return HttpResponse(json.dumps({"success": success}))


def do_delete_rm(request):
    """
    do_delete_rm
    """
    success = False
    valid_user = token_checker.token_is_valid(request)
    if valid_user and "id" in request.GET and ArgsChecker.is_number(request.GET["id"]):
        try:
            ff = FinalFusion.objects.get(project=Project.objects.get(pk=valid_user.last_opened_project_id))
            rm = RuleModule.objects.get(pk=request.GET["id"], final_fusion=ff)
            rm.archived = True
            rm.save()
            success = True
        except ObjectDoesNotExist:
            pass
    return HttpResponse(json.dumps({"success": success}))


def do_save_edit(request):
    """
    do_save_edit
    """
    success = False
    valid_user = token_checker.token_is_valid(request)
    if valid_user and "id" in request.GET and ArgsChecker.is_number(request.GET["id"]) \
            and rule_condition_check(request):

        rm = request_to_rm(request, request.GET["id"])
        rm.save()
        if rm:
            success = True

    return HttpResponse(json.dumps({"success": success}))


def render_all_rm(request):
    """
    render_all_rm
    """
    success = False
    ret = []

    valid_user = token_checker.token_is_valid(request)
    if valid_user:
        success = True
        proj = Project.objects.get(pk=valid_user.last_opened_project_id)
        ff = FinalFusion.objects.get(project=proj)
        rule_modules = RuleModule.objects.filter(final_fusion=ff, archived=False)

        for rm in rule_modules:
            item = {
                "id": rm.pk,
                "name": rm.name,
                "type": rm.rule_type
            }

            if rm.rule_type == "col":
                item["subject_name"] = FinalFusionColumn.objects.get(pk=json.loads(rm.subjects)[0]).display_column_name

                col_if_condition = json.loads(rm.if_conditions)
                item["when_type"] = list(col_if_condition.keys())[0].upper().split("_")[1]
                item["when_value"] = col_if_condition[list(col_if_condition.keys())[0]]

                then_case = json.loads(rm.then_cases)
                item["then_type"] = list(then_case.keys())[0].upper().split("_")[1]
                item["then_value"] = then_case[list(then_case.keys())[0]]

                ret.append(item)

    return HttpResponse(json.dumps({
        "success": success,
        "items": json.dumps(ret)
    }))
