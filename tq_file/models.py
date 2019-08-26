from django.db import models
from django.utils import timezone
from project.models import Project


class TQFile(models.Model):
    """
    Model which holds data of already parsed files.
    """
    creation_date = models.DateTimeField(default=timezone.now)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    source_file_name = models.CharField(max_length=100)
    display_file_name = models.CharField(max_length=50)
    content_json = models.TextField()

    def __str__(self):
        return "#%d: %s" % (self.pk, self.display_file_name)