import json
from django.shortcuts import render
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.models import User, Group
from security.args_checker import ArgsChecker
from user_profile.models import UserProfile


def render_login(request):
    """
    render_login
    """
    return render(request, "user_profile/login.html")


def render_signup(request):
    """
    Will render the sign up view to make new registrations possible.
    """
    return render(request, "user_profile/signup.html")


def render_settings(request):
    """
    render_settings
    """
    rendered = render_to_string("user_profile/_settings.html")
    return HttpResponse(json.dumps(
        {
            "html": str(rendered)
        }))


def do_sign_up(request):
    """
    do_sign_up
    """
    success = False
    msg = ""
    token = None

    if "email" in request.POST and not ArgsChecker.str_is_malicious(request.POST["email"]) \
            and "pw1" in request.POST and not ArgsChecker.str_is_malicious(request.POST["pw1"]) \
            and "pw2" in request.POST and not ArgsChecker.str_is_malicious(request.POST["pw2"]):

        email = request.POST["email"]
        pw1 = request.POST["pw1"]
        pw2 = request.POST["pw2"]

        if "@daimler.com" not in email:
            msg = "Email not from company"
        elif pw1 != pw2:
            msg = "Passwords don't match"
        elif len(pw1) < 8:
            msg = "Password too short"
        else:
            if len(User.objects.filter(email=email)) == 0:
                try:
                    user = User.objects.create(
                        email=email,
                        password=make_password(pw1))

                    user_group = Group.objects.get(name='Users')
                    user_group.user_set.add(user)
                    token = UserProfile.objects.get(user=user).token.code
                    success = True
                except Exception as exc:
                    print(exc)
            else:
                msg = "User already existing"

    response = HttpResponse(json.dumps(
        {
            "success": success,
            "msg": msg
        }))

    response.set_cookie("token", token, max_age=86400 * 7)
    return response
