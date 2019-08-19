from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from security_token.models import SecurityToken


class UserProfile(models.Model):
    """
    Created automatically with a new user-model.
    RuleModules can be linked to this model.
    """
    creation_date = models.DateTimeField(default=timezone.now)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.ForeignKey(SecurityToken,
                              related_name='%(class)s_cookie_token',
                              on_delete=models.CASCADE, null=True)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = UserProfile.objects.create(user=instance)

        token = SecurityToken()
        token.generate_token_code()
        token.save()

        profile.token = token
        profile.save()
