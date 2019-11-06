import json
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from security.args_checker import ArgsChecker
import security.token_checker as token_checker
from project.models import Project
from final_fusion.models import FinalFusion
from script_module.models import ScriptModule


def do_validate_code(request):
    """
    Will check whether the passed code (by request) is valid script code.
    Creates a temporary script module and will return the result of its validation method.
    """
    valid_user = token_checker.token_is_valid(request)

    if valid_user and "code" in request.POST:
        proj = Project.objects.get(pk=valid_user.last_opened_project_id)
        ff = FinalFusion.objects.get(project=proj)

        sm = ScriptModule()
        sm.code_content = request.POST["code"]
        sm.final_fusion = ff

        return HttpResponse(json.dumps(sm.check_validity()))


def do_create(request):
    """
    Will create a script module based on the passed information from the web request.
    The rule module will only be saved if its code is valid.
    """
    sucess = False
    valid_user = token_checker.token_is_valid(request)

    if valid_user and "code" in request.POST:
        proj = Project.objects.get(pk=valid_user.last_opened_project_id)
        ff = FinalFusion.objects.get(project=proj)

        sm = ScriptModule()
        sm.code_content = request.POST["code"]
        sm.final_fusion = ff
        res = sm.check_validity()

        if res["valid"]:
            sm.save()
            sucess = True

    return HttpResponse(json.dumps({"success": sucess}))


def do_edit(request):
    """
    Will edit a rule module by overriding the differences.
    """
    sucess = False
    valid_user = token_checker.token_is_valid(request)

    if valid_user and "code" in request.POST and "id" in request.POST and ArgsChecker.is_number(request.POST["id"]):
        try:
            sm = ScriptModule.objects.get(pk=request.POST["id"], archived=False)
            sm.code_content = request.POST["code"]
            sm.save()
        except ObjectDoesNotExist:
            pass
        sucess = True

    return HttpResponse(json.dumps({"success": sucess}))


def do_delete_sm(request):
    """
    Will delete this rule module by archiving.
    """
    success = False
    valid_user = token_checker.token_is_valid(request)
    if valid_user and "id" in request.GET and ArgsChecker.is_number(request.GET["id"]):
        try:
            ff = FinalFusion.objects.get(project=Project.objects.get(pk=valid_user.last_opened_project_id))
            sm = ScriptModule.objects.get(pk=request.GET["id"], final_fusion=ff)
            sm.archived = True
            sm.save()
            success = True
        except ObjectDoesNotExist:
            pass
    return HttpResponse(json.dumps({"success": success}))


def render_single(request):
    """
    Will render a single script-rm for the UI.
    """
    success = False
    single = None

    valid_user = token_checker.token_is_valid(request)
    if valid_user and "id" in request.GET and ArgsChecker.is_number(request.GET["id"]):
        try:
            sm = ScriptModule.objects.get(pk=request.GET["id"], archived=False)
            success = True
            single = {
                "name": sm.name,
                "code_content": sm.code_content
            }
        except ObjectDoesNotExist:
            pass

    return HttpResponse(json.dumps({
        "success": success,
        "obj": json.dumps(single)
    }))
