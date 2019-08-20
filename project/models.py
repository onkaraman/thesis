from django.db import models
from django.utils import timezone
from user_profile.models import UserProfile


class Project(models.Model):
    """
    Project
    """
    creation_date = models.DateTimeField(default=timezone.now)
    name = models.CharField(max_length=100)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return "#%d: %s" % (self.pk, self.name)