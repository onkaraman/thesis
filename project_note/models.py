from django.db import models
from django.utils import timezone
from project.models import Project


class ProjectNote(models.Model):
    """
    ProjectNote
    """
    creation_date = models.DateTimeField(default=timezone.now)
    archived = models.BooleanField(default=False)
    name = models.CharField(max_length=50)
    content = models.TextField(max_length=500)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return "#%d: %s" % (self.pk, self.name)
