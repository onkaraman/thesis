import json
from django.http import HttpResponse
from security.args_checker import ArgsChecker
import security.token_checker as token_checker
from django.core.exceptions import ObjectDoesNotExist
from final_fusion_column.models import FinalFusionColumn
from rule_module.models import RuleModule


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


def do_create_col_rm(request):
    """
    do_create_col_rm
    """
    success = False
    valid_user = token_checker.token_is_valid(request)
    if valid_user and "when_is" in request.GET and "when_contains" in request.GET \
            and "when_value" in request.GET and not ArgsChecker.str_is_malicious(request.GET["when_value"]) \
            and "then_apply" in request.GET and "then_replace" in request.GET \
            and "then_value" in request.GET and not ArgsChecker.str_is_malicious(request.GET["then_value"]) \
            and "subject_id" in request.GET and ArgsChecker.is_number(request.GET["subject_id"]):

        get_params = convert_request_bool_values(request.GET)

        subject_id = get_params["subject_id"]
        when_is = get_params["when_is"]
        when_contains = get_params["when_contains"]
        when_value = get_params["when_value"]
        then_apply = get_params["then_apply"]
        then_replace = get_params["then_replace"]
        then_value = get_params["then_value"]

        rm = RuleModule()

        if len(when_value) > 0 and len(then_value) > 0:
            try:
                ffc = FinalFusionColumn.objects.get(pk=subject_id)
                rm.rule_type = "col"
                rm.subjects = json.dumps([ffc.pk])

                if ((when_is and not when_contains) or (not when_is and when_contains)) \
                        and ((then_apply and not then_replace) or (not then_apply and then_replace)) \
                        and (when_is and not then_replace):

                    # Construct if condition
                    if_condition = {}
                    if when_is:
                        if_condition["when_is"] = when_value
                    elif when_contains:
                        if_condition["when_contains"] = when_value
                    print(if_condition)

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
                    rm.save()
                    success = True

            except ObjectDoesNotExist:
                pass

    return HttpResponse(json.dumps({"success": success}))
