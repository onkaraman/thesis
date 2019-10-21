import json
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from security.args_checker import ArgsChecker
import security.token_checker as token_checker
from project.models import Project
from project_note.models import ProjectNote


def do_create(request):
    """
    do_create
    """
    success = False
    valid_user = token_checker.token_is_valid(request)

    if valid_user and "name" in request.GET and not ArgsChecker.str_is_malicious(request.GET["name"]) \
        and "content" in request.GET and not ArgsChecker.str_is_malicious(request.GET["content"]):

        ProjectNote.objects.create(
            name=request.GET["name"],
            content=request.GET["content"],
            project=Project.objects.get(pk=valid_user.last_opened_project_id, archived=False)
        )
        success = True

    return HttpResponse(json.dumps(
        {
            "success": success,
        }))


def do_delete(request):
    """
    do_delete
    """
    success = False
    valid_user = token_checker.token_is_valid(request)

    if valid_user and "id" in request.GET and ArgsChecker.is_number(request.GET["id"]):
        try:
            n = ProjectNote.objects.get(pk=request.GET["id"])
            n.archived = True
            n.save()
            success = True
        except ObjectDoesNotExist:
            pass

    return HttpResponse(json.dumps(
        {
            "success": success,
        }))


def render_all(request):
    """
    render_all
    """
    valid_user = token_checker.token_is_valid(request)
    items = []

    if valid_user:
        proj = Project.objects.get(pk=valid_user.last_opened_project_id)
        notes = ProjectNote.objects.filter(project=proj, archived=False)
        for n in notes:
            items.append({
                "id": n.pk,
                "name": n.name,
                "content": n.content
            })
    return HttpResponse(json.dumps(
        {
            "items": items,
        }))