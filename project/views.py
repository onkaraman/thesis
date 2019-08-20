import json
from django.shortcuts import render
from django.http import HttpResponse
from .models import Project
import security.token_checker as token_checker


def do_create_new(request):
    """
    do_create_new
    """
    success = False
    name = None

    valid_user = token_checker.token_is_valid(request)
    if valid_user:
        proj = Project.objects.create(name="Fusion Project %d"
                                           % (len(Project.objects.filter(user_profile=valid_user))),
                                      user_profile=valid_user)

        valid_user.last_opened_project_id = proj.pk
        valid_user.save()
        success = True
        name = proj.name

    return HttpResponse(json.dumps(
        {
            "success": success,
            "name": name
        }))