from django.db import models
from django.utils import timezone
from project.models import Project


class FinalFusion(models.Model):
    """
    FinalFusion
    """
    creation_date = models.DateTimeField(default=timezone.now)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return "#%d: EF" % self.pk
