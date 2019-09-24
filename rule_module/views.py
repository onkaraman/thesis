import json
from django.http import HttpResponse
from security.args_checker import ArgsChecker
import security.token_checker as token_checker
from django.core.exceptions import ObjectDoesNotExist
from final_fusion.models import FinalFusion
from final_fusion_column.models import FinalFusionColumn
from rule_module.models import RuleModule
from project.models import Project
from rule_module import  rule_queue as rule_queue


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


def col_rule_condition_check(request):
    """
    col_rule_condition_check
    """
    if "when_is" in request.GET and "when_contains" in request.GET \
            and "when_value" in request.GET and not ArgsChecker.str_is_malicious(request.GET["when_value"]) \
            and "then_apply" in request.GET and "then_replace" in request.GET \
            and "then_value" in request.GET and not ArgsChecker.str_is_malicious(request.GET["then_value"]) \
            and "subject_id" in request.GET and ArgsChecker.is_number(request.GET["subject_id"]):
        return True
    return False


def request_to_col_rm(request, id=None):
    """
    request_to_col_rm
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

    if len(when_value) > 0 and len(then_value) > 0:
        try:
            ffc = FinalFusionColumn.objects.get(pk=subject_id)
            rm.rule_type = "col"
            rm.col_subject = json.dumps([ffc.pk])

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
    if valid_user and col_rule_condition_check(request):
        rm = request_to_col_rm(request)
        rm.save()
        if rm:
            success = True

    return HttpResponse(json.dumps({"success": success}))


def data_to_row_rm(when_data, then_data, existing_id=None):
    """
    data_to_row_rm
    """
    rm = RuleModule()
    if existing_id:
        rm = RuleModule.objects.get(pk=existing_id)
    else:
        rm.name = "Zeilenregel %d " % (len(when_data) + len(then_data))
        rm.rule_type = "row"

    if_cond = []
    then_cases = []

    for and_bracket in when_data:
        to_add = []
        for wd in and_bracket:
            ffc = FinalFusionColumn.objects.filter(pk=wd["id"])
            if len(ffc) == 1 and (wd["condition"] == "IS" or wd["condition"] == "CONTAINS") and len(wd["value"]) > 0:
                wd["ffc_name"] = ffc[0].display_column_name
                to_add.append(wd)
        if_cond.append(to_add)

    for td in then_data:
        ffc = FinalFusionColumn.objects.filter(pk=td["id"])
        if len(ffc) == 1 and (td["action"] == rule_queue.APPLY
                              or td["action"] == rule_queue.REPLACE) and len(td["value"]) > 0:
            td["ffc_name"] = ffc[0].display_column_name
            then_cases.append(td)

    rm.final_fusion = FinalFusionColumn.objects.get(id=when_data[0][0]["id"]).final_fusion
    rm.if_conditions = json.dumps(if_cond)
    rm.then_cases = json.dumps(then_cases)
    rm.save()
    return rm


def do_create_row_rm(request):
    """
    do_create_row_rm
    """
    success = False
    valid_user = token_checker.token_is_valid(request)
    if valid_user and "when_data" in request.GET and "then_data" in request.GET:

        try:
            when_data = json.loads(request.GET["when_data"])
            then_data = json.loads(request.GET["then_data"])
            rm = data_to_row_rm(when_data, then_data)
            if rm:
                success = True
        except TypeError:
            print("do_create_row_rm: TypeError")

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


def do_save_edit_col(request):
    """
    do_save_edit_col
    """
    success = False
    valid_user = token_checker.token_is_valid(request)
    if valid_user and "id" in request.GET and ArgsChecker.is_number(request.GET["id"]) \
            and col_rule_condition_check(request):

        rm = request_to_col_rm(request, request.GET["id"])
        rm.save()
        if rm:
            success = True

    return HttpResponse(json.dumps({"success": success}))


def do_save_edit_row(request):
    """
    do_save_edit_col
    """
    success = False
    valid_user = token_checker.token_is_valid(request)
    if valid_user and "id" in request.GET and ArgsChecker.is_number(request.GET["id"]):

        try:
            when_data = json.loads(request.GET["when_data"])
            then_data = json.loads(request.GET["then_data"])
            rm = data_to_row_rm(when_data, then_data, request.GET["id"])
            if rm:
                success = True
        except TypeError as te:
            print("do_create_row_rm: TypeError")

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

            ret.append(item)

    return HttpResponse(json.dumps({
        "success": success,
        "items": json.dumps(ret)
    }))


def render_single(request):
    """
    render_single
    """
    success = False
    single = None

    valid_user = token_checker.token_is_valid(request)
    if valid_user and "id" in request.GET and ArgsChecker.is_number(request.GET["id"]):
        try:
            rm = RuleModule.objects.get(pk=request.GET["id"], archived=False)
            success = True
            single = {
                "name": rm.name,
                "type": rm.rule_type,
                "if_conditions": rm.if_conditions,
                "then_cases": rm.then_cases
            }

            if rm.rule_type == "col":
                ffc = FinalFusionColumn.objects.get(pk=json.loads(rm.col_subject)[0])
                single["col_subject_name"] = ffc.display_column_name
                single["col_subject_id"] = ffc.pk
        except ObjectDoesNotExist:
            pass

    return HttpResponse(json.dumps({
        "success": success,
        "obj": json.dumps(single)
    }))