import json
from datetime import datetime
from django.utils.timezone import utc
from django.http import HttpResponse
from .models import Project
import security.token_checker as token_checker
import dashboard.includer as dashboard_includer
from django.core.exceptions import ObjectDoesNotExist
from security.args_checker import ArgsChecker
from tq_file.models import TQFile
from final_fusion.models import FinalFusion
from rule_module.models import RuleModule
from script_module.models import ScriptModule


def do_create_new(request):
    """
    do_create_new
    """
    success = False
    name = None

    valid_user = token_checker.token_is_valid(request)
    if valid_user:
        number = len(Project.objects.filter(user_profile=valid_user))
        project = Project.objects.create(name="Fusion Project %d" % number,
                                         user_profile=valid_user)
        FinalFusion.objects.create(project=project)

        valid_user.last_opened_project_id = project.pk
        valid_user.save()
        success = True
        name = project.name

    return HttpResponse(json.dumps(
        {
            "success": success,
            "name": name
        }))


def do_load(request):
    """
    do_load
    """
    success = False
    name = None

    valid_user = token_checker.token_is_valid(request)
    if valid_user and "id" in request.GET and ArgsChecker.is_number(request.GET["id"]):
        project = Project.objects.get(pk=request.GET["id"])
        valid_user.last_opened_project_id = project.pk
        valid_user.save()

        success = True
        name = project.name
    return HttpResponse(json.dumps(
        {
            "success": success,
            "name": name
        }))


def do_autoload(request):
    """
    do_autoload
    """
    success = False
    proj_id = None

    valid_user = token_checker.token_is_valid(request)
    if valid_user:
        try:
            project = Project.objects.get(pk=valid_user.last_opened_project_id, archived=False)
            proj_id = project.pk
            success = True
        except ObjectDoesNotExist:
            pass
    return HttpResponse(json.dumps(
        {
            "success": success,
            "id": proj_id
        }))


def do_rename(request):
    """
    do_rename
    """
    success = False
    valid_user = token_checker.token_is_valid(request)

    if valid_user and "name" in request.GET and not ArgsChecker.str_is_malicious(request.GET["name"]):
        project = Project.objects.get(pk=valid_user.last_opened_project_id)
        project.name = request.GET["name"]
        project.save()
        success = True

    return HttpResponse(json.dumps({"success": success}))


def do_delete_project(request):
    """
    do_delete_project
    """
    success = False
    valid_user = token_checker.token_is_valid(request)
    if valid_user:
        if "id" in request.GET and ArgsChecker.is_number(request.GET["id"]):
            try:
                project = Project.objects.get(pk=request.GET["id"], user_profile=valid_user)
                project.archived = True
                project.save()
                success = True
            except ObjectDoesNotExist:
                pass
    return HttpResponse(json.dumps({"success": success}))


def i_render_user_projects(request):
    """
    render_overview
    """
    valid_user = token_checker.token_is_valid(request)
    dic = {}
    if valid_user:
        projects = Project.objects.filter(user_profile=valid_user, archived=False)
        project_list = []
        for p in projects:
            ff = FinalFusion.objects.get(project=p)

            rm_count = len(RuleModule.objects.filter(final_fusion=ff, archived=False))
            rm_count += len(ScriptModule.objects.filter(final_fusion=ff, archived=False))

            project_list.append({
                "id": p.pk,
                "name": p.name,
                "tq_len": len(TQFile.objects.filter(project=p, archived=False)),
                "rm_len": rm_count,
                "date": "Erstellt am %s" % p.creation_date.strftime('%d.%m.%Y'),
            })

        dic["projects"] = project_list
        return dashboard_includer.get_as_json("project/_user_projects.html", template_context=dic)


def i_render_new_project(request):
    """
    i_render_new_project
    """
    valid_user = token_checker.token_is_valid(request)
    if valid_user:
        return dashboard_includer.get_as_json("project/_new_project.html")


def render_project_details(request):
    """
    render_project_details
    """
    success = False

    valid_user = token_checker.token_is_valid(request)
    if valid_user:
        try:
            project = Project.objects.get(pk=valid_user.last_opened_project_id, archived=False)
            c_date = project.creation_date.strftime('%d.%m.%Y')
            days_past = datetime.utcnow().replace(tzinfo=utc) - project.creation_date.replace(tzinfo=utc)

            return HttpResponse(json.dumps(
                {
                    "success": True,
                    "creation_date": str(c_date),
                    "days_past": days_past.days,
                }))

        except ObjectDoesNotExist:
            pass

    return HttpResponse(json.dumps(
        {
            "success": success,
        }))
