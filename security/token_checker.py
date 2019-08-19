from django.core.exceptions import ObjectDoesNotExist
from user_profile.models import UserProfile
from .string_stripper import StringStripper


def token_is_valid(request):
    """
    token_is_valid
    """
    if "token" in request.COOKIES:
        token = StringStripper.remove_malicious(request.COOKIES["token"])
        try:
            user = UserProfile.objects.get(token__code=token)
            if not user.token.has_expired():
                return user
        except ObjectDoesNotExist:
            return False