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
    do_validate_code
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
    do_create
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