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
            user_profile = UserProfile.objects.get(token__code=token)
            if not user_profile.token.has_expired():
                return user_profile
        except ObjectDoesNotExist:
            return False