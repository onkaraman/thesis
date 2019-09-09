from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
import security.token_checker as token_checker
from final_fusion.models import FinalFusion
from project.models import Project


def render_dashboard(request):
    """
    render_dashboard
    """
    dic = {}
    valid_user = token_checker.token_is_valid(request)
    if valid_user:
        proj = Project.objects.get(pk=valid_user.last_opened_project_id)
        ff = FinalFusion.objects.get(project=proj)

        dic["username"] = valid_user.user.email
        dic["ef_name"] = ff.name

        return render(request, "dashboard/dashboard.html", dic)
    else:
        return HttpResponseRedirect(reverse("login"))
