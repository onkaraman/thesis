import json
from django.shortcuts import render
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User, Group
from security.args_checker import ArgsChecker
import security.token_checker as token_checker
import dashboard.includer as dashboard_includer
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


def i_render_settings(request):
    """
    i_render_settings
    """
    valid_user = token_checker.token_is_valid(request)
    if valid_user:
        return dashboard_includer.get_as_json("user_profile/_settings.html",
                                              different_js="_user_settings.js")


def do_login(request):
    success = False
    msg = ""

    user = None
    pw_correct = False

    if "email" in request.POST and not ArgsChecker.str_is_malicious(request.POST["email"]) \
            and "pw" in request.POST and not ArgsChecker.str_is_malicious(request.POST["pw"]):

        email = request.POST["email"]
        pw = request.POST["pw"]

        if "@daimler.com" not in email:
            msg = "Email not from company"
        elif len(pw) < 8:
            msg = "Password too short"
        else:
            try:
                user = UserProfile.objects.get(user__email=email)
                if check_password(pw, user.user.password):
                    user.token.generate_token_code()
                    pw_correct = True
                    success = True
            except ObjectDoesNotExist:
                msg = "User not registered"

    response = HttpResponse(json.dumps(
        {
            "success": success,
            "msg": msg
        }))

    if pw_correct:
        response.set_cookie("token", user.token.code, max_age=86400 * 7)
    return response


def do_logout(request):
    """
    do_logout
    """
    valid_user = token_checker.token_is_valid(request)

    if valid_user:
        response = HttpResponse(json.dumps({ "success": True }))
        response.set_cookie("token", None)
        return response
    else:
        return HttpResponse(json.dumps({"success": False}))


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
                        username=email,
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
