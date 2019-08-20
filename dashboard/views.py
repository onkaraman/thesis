from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
import security.token_checker as token_checker


def render_dashboard(request):
    """
    render_dashboard
    """
    dic = {}
    valid_user = token_checker.token_is_valid(request)
    if valid_user:
        dic["username"] = valid_user.user.email
        return render(request, "dashboard/dashboard.html", dic)
    else:
        return HttpResponseRedirect(reverse("login"))
