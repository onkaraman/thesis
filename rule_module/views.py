import json
from django.http import HttpResponse
from security.args_checker import ArgsChecker
import security.token_checker as token_checker
from django.core.exceptions import ObjectDoesNotExist
from final_fusion.models import FinalFusion
from final_fusion_column.models import FinalFusionColumn
from rule_module.models import RuleModule
from script_module.models import ScriptModule
from project.models import Project
from rule_module import rule_queue as rule_queue


def convert_request_bool_values(get_params):
    """
    Helper method. Will convert strings like 'true' to actual True values.
    """
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
    Will check whether the conditions of a column-rm are contentually correct.
    """
    if "when_is" in request.GET and "when_contains" in request.GET \
            and "when_value" in request.GET and not ArgsChecker.str_is_malicious(request.GET["when_value"]) \
            and "then_apply" in request.GET and "then_replace" in request.GET \
            and "then_value" in request.GET and not ArgsChecker.str_is_malicious(request.GET["then_value"]) \
            and "subject_id" in request.GET and ArgsChecker.is_number(request.GET["subject_id"]):
        return True
    return False


def request_to_col_rm(request, _id=None):
    """
    :param request: The request from the rule module UI.
    :param _id: Is not none when this is a edit-case. If edit, only changes will be overridden.

    Will turn a web request for a column-rm to an actual rule module object.
    """
    get_params = convert_request_bool_values(request.GET)

    subject_id = get_params["subject_id"]

    when_is = get_params["when_is"]
    name = get_params["name"]
    when_contains = get_params["when_contains"]
    when_value = get_params["when_value"]
    then_apply = get_params["then_apply"]
    then_replace = get_params["then_replace"]
    then_value = get_params["then_value"]

    rm = RuleModule()
    if _id:
        rm = RuleModule.objects.get(pk=_id)

    if len(when_value) > 0 and len(then_value) > 0:
        try:
            ffc = FinalFusionColumn.objects.get(pk=subject_id)
            rm.rule_type = "col"
            rm.col_subject = json.dumps([ffc.pk])

            if not ArgsChecker.str_is_malicious(name) and ((when_is and not when_contains) or (not when_is and when_contains)) \
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
                rm.name = name
                return rm

        except ObjectDoesNotExist:
            return None


def do_create_col_rm(request):
    """
    Will create a column rule module from the web request.
    """
    success = False
    valid_user = token_checker.token_is_valid(request)
    if valid_user and col_rule_condition_check(request):
        rm = request_to_col_rm(request)
        rm.save()
        if rm:
            success = True

    return HttpResponse(json.dumps({"success": success}))


def create_dynamic_column(name, ff):
    """
    :param name: The name of this FFC.
    :param ff: The final fusion this column will be attached to.
    Will create a dynamic column for a row-rm.
    """
    # Make sure shit won't get created multiple times
    ffc = FinalFusionColumn()
    ffc.final_fusion = ff
    ffc.source_column_name = name
    ffc.display_column_name = name
    ffc.rows_json = json.dumps([])
    return ffc


def data_to_row_rm(when_data, then_data, existing_id=None):
    """
    Will turn a web request to create a column-rm to an actual col-rm.
    :param when_data: The when-data, configrued via UI.
    :param then_data: Then-data, configured via UI.
    :param existing_id: If not None, this is an edit case in which only changes of the rm will be overridden.
    """
    ff = FinalFusionColumn.objects.get(id=when_data[0][0]["id"]).final_fusion
    rm = RuleModule()

    if existing_id:
        rm = RuleModule.objects.get(pk=existing_id)
    else:
        rm.name = "Neue Zeilenregel"
        rm.rule_type = "row"

    if_cond = []
    then_cases = []

    # And-Brackets are conditions between or-seperators of the UI.
    for and_bracket in when_data:
        to_add = []
        for wd in and_bracket:
            ffc = FinalFusionColumn.objects.filter(pk=wd["id"])
            if len(ffc) == 1 and (wd["condition"] == "IS" or wd["condition"] == "CONTAINS") and len(wd["value"]) > 0:
                wd["ffc_name"] = ffc[0].display_column_name
                to_add.append(wd)
        if_cond.append(to_add)

    # Items in this list will be FFCs wich depend on this rm.
    dependencies = []
    for td in then_data:
        ffc = None

        if "id" in td and int(td["id"]) == -1:
            ffc = create_dynamic_column(td["dyn_col"], ff)
            td["was_dynamic"] = True
            dependencies.append(ffc)
        elif "id" in td:
            ffc = FinalFusionColumn.objects.get(pk=td["id"])

            if "was_dynamic" in td and td["was_dynamic"]:
                dependencies.append(ffc)

            if ffc.archived and td["was_dynamic"]:
                ffc.archived = False
                ffc.save()

        if ffc and (td["action"] == rule_queue.APPLY or td["action"] == rule_queue.REPLACE) and len(td["value"]) > 0:
            td["ffc_name"] = ffc.display_column_name
            if len(td["dyn_col"]) > 0:
                td["ffc_name"] = td["dyn_col"]
                ffc.display_column_name = td["dyn_col"]

            then_cases.append(td)
        elif td["action"] == rule_queue.IGNORE:
            then_cases.append(td)

    rm.final_fusion = ff
    rm.if_conditions = json.dumps(if_cond)
    rm.then_cases = json.dumps(then_cases)
    rm.save()

    for dep_ffc in dependencies:
        dep_ffc.rm_dependency = rm
        dep_ffc.save()
        # Reapply the FFC ID
        for tc in then_cases:
            if "ffc_name" in tc and tc["ffc_name"] == dep_ffc.display_column_name:
                td["id"] = dep_ffc.pk
                rm.then_cases = json.dumps(then_cases)
                rm.save()
    return rm


def do_create_row_rm(request):
    """
    Will take a user request to create a row-rm to create an actual rm via 'data_to_row_rm()'.
    """
    success = False
    valid_user = token_checker.token_is_valid(request)
    if valid_user and "when_data" in request.GET and "then_data" in request.GET:

        try:
            when_data = json.loads(request.GET["when_data"])
            then_data = json.loads(request.GET["then_data"])
            try:
                rm = data_to_row_rm(when_data, then_data)
                if rm:
                    success = True
            except Exception:
                pass
        except TypeError:
            print("do_create_row_rm: TypeError")

    return HttpResponse(json.dumps({"success": success}))


def do_delete_rm(request):
    """
    Will delete a rule module by archiving.
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


def do_rename_rm(request):
    """
    Will rename a rule module.
    """
    success = False
    valid_user = token_checker.token_is_valid(request)

    if valid_user and "name" in request.GET and not ArgsChecker.str_is_malicious(request.GET["name"]) \
            and "id" in request.GET and ArgsChecker.is_number(request.GET["id"]) \
            and "type" in request.GET and not ArgsChecker.str_is_malicious(request.GET["type"]):
        try:
            rm = None

            if request.GET["type"] == "rm":
                rm = RuleModule.objects.get(pk=request.GET["id"])
            elif request.GET["type"] == "script":
                rm = ScriptModule.objects.get(pk=request.GET["id"])

            rm.name = request.GET["name"]
            rm.save()
            success = True
        except ObjectDoesNotExist:
            pass
    return HttpResponse(json.dumps({"success": success}))


def do_save_edit_col(request):
    """
    Will edit a col-rm by taking the existing one and overriding the new changes.
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
    Will edit a row-rm by taking the existing one and overriding the new changes.
    """
    success = False
    valid_user = token_checker.token_is_valid(request)
    if valid_user and "id" in request.GET and ArgsChecker.is_number(request.GET["id"]) \
            and "when_data" in request.GET and "then_data" in request.GET:

        try:
            when_data = json.loads(request.GET["when_data"])
            then_data = json.loads(request.GET["then_data"])
            rm = data_to_row_rm(when_data, then_data, request.GET["id"])
            if rm:
                success = True
        except TypeError as te:
            print("do_create_row_rm: TypeError")

    return HttpResponse(json.dumps({"success": success}))


def do_transfer_rm(request):
    """
    Will take a rule module from another project to add it to the current project.
    """
    success = False
    valid_user = token_checker.token_is_valid(request)

    if valid_user and "id" in request.GET and ArgsChecker.is_number(request.GET["id"]):
        rm_id = request.GET["id"]

        proj = Project.objects.get(pk=valid_user.last_opened_project_id)
        ff = FinalFusion.objects.get(project=proj)

        try:
            rm = RuleModule.objects.get(pk=rm_id)
            rm.pk = None
            rm.final_fusion = ff
            rm.save()
            success = True
        except ObjectDoesNotExist as exc:
            pass

    return HttpResponse(json.dumps({"success": success}))


def render_all_rm(request):
    """
    Will return a JSON-Object containing all rule modules of the currently opened project/TF.
    """
    success = False
    ret = []

    valid_user = token_checker.token_is_valid(request)
    if valid_user:
        success = True
        proj = Project.objects.get(pk=valid_user.last_opened_project_id)
        ff = FinalFusion.objects.get(project=proj)
        rule_modules = RuleModule.objects.filter(final_fusion=ff, archived=False).order_by("pk")
        script_modules = ScriptModule.objects.filter(final_fusion=ff, archived=False).order_by("pk")

        types_display = {
            "col": "COL",
            "row": "ROW",
            "script": "SCR"
        }

        for rm in rule_modules:
            ret.append({
                "id": rm.pk,
                "name": rm.name,
                "type": rm.rule_type,
                "type_display": types_display[rm.rule_type],
                "is_valid": rm.is_valid()

            })

        for sm in script_modules:
            ret.append({
                "id": sm.pk,
                "name": sm.name,
                "type": "script",
                "type_display": types_display["script"],
                "is_valid": sm.check_validity()["valid"]
            })

    return HttpResponse(json.dumps({
        "success": success,
        "items": json.dumps(ret)
    }))


def render_filtered(request):
    """
    Will render rule modules which contain 'filter_name' in their names. Used for rm-search.
    """
    success = False
    items = []

    valid_user = token_checker.token_is_valid(request)

    if valid_user and "filter" in request.GET and not ArgsChecker.str_is_malicious(request.GET["filter"]):
        success = True
        filter_name = request.GET["filter"].strip()

        types_display = {
            "col": "COL",
            "row": "ROW",
            "script": "SCR"
        }

        projects = Project.objects.filter(user_profile=valid_user, archived=False)
        for p in projects:
            ff = FinalFusion.objects.get(project=p)
            rule_modules = RuleModule.objects.filter(final_fusion=ff, archived=False)
            script_modules = ScriptModule.objects.filter(final_fusion=ff, archived=False)

            for rm in rule_modules:
                if filter_name.lower() in rm.name.lower():
                    items.append({
                        "project_name": p.name,
                        "id": rm.pk,
                        "name": rm.name,
                        "type": rm.rule_type,
                        "type_display": types_display[rm.rule_type]
                    })

            for sm in script_modules:
                if filter_name in sm.name:
                    items.append({
                        "project_name": p.name,
                        "id": sm.pk,
                        "name": sm.name,
                        "type": "script",
                        "type_display": types_display["script"]
                    })

    return HttpResponse(json.dumps({
        "success": success,
        "items": json.dumps(items)
    }))


def render_single(request):
    """
    Will return a JSON-Object of details about the current rm.
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
                "then_cases": rm.then_cases,
                "dynamic": False
            }

            if rm.rule_type == "col":
                ffc = FinalFusionColumn.objects.get(pk=json.loads(rm.col_subject)[0])
                single["col_subject_name"] = ffc.display_column_name
                single["col_subject_id"] = ffc.pk

            elif rm.rule_type == "row":
                try:
                    FinalFusionColumn.objects.get(rm_dependency=rm)
                    single["dynamic"] = True
                except Exception:
                    pass

        except ObjectDoesNotExist:
            pass

    return HttpResponse(json.dumps({
        "success": success,
        "obj": json.dumps(single)
    }))