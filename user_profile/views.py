from django.shortcuts import render


def sign_up(request):
    """
    Will render the sign up view to make new registrations possible.
    """
    return render(request, "user_profile/sign_up.html")