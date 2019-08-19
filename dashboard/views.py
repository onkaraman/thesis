from django.shortcuts import render
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
