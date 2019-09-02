import json
from django.db import models
from django.utils import timezone
from project.models import Project


class TQFile(models.Model):
    """
    Model which holds data of already parsed files.
    """
    creation_date = models.DateTimeField(default=timezone.now)
    archived = models.BooleanField(default=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    source_file_name = models.CharField(max_length=100)
    display_file_name = models.CharField(max_length=50)
    content_json = models.TextField()

    def get_as_table(self):
        """
        get_as_table
        """
        loaded_js = json.loads(self.content_json)
        columns = ["#"]

        for row in loaded_js:
            for i in row:
                if i not in columns:
                    columns.append(i)
        return {
            "cols": columns,
            "rows": loaded_js,
            "items": len(loaded_js)
        }

    def get_column(self, col_name):
        """
        get_column
        """
        loaded_js = json.loads(self.content_json)
        ret = []
        for row in loaded_js:
            ret.append(row[col_name])
        return ret

    def __str__(self):
        return "#%d: %s" % (self.pk, self.display_file_name)