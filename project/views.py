import json
from django.http import HttpResponse
from .models import Project
import security.token_checker as token_checker
from security.args_checker import ArgsChecker


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

        valid_user.last_opened_project_id = project.pk
        valid_user.save()
        success = True
        name = project.name

    return HttpResponse(json.dumps(
        {
            "success": success,
            "name": name
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
