import json
from django.db import models
from django.utils import timezone
from project.models import Project
from final_fusion.models import FinalFusion


class TQFile(models.Model):
    """
    Model which holds data of already parsed files.
    """
    creation_date = models.DateTimeField(default=timezone.now)
    archived = models.BooleanField(default=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    source_file_name = models.CharField(max_length=100)
    display_file_name = models.CharField(max_length=50)
    has_been_flattened = models.BooleanField(default=False)
    content_json = models.TextField()

    def get_as_table(self, user_profile):
        """
        :return All columns and rows of this parsed TQ as a dictionary.
        Will also check if each row is already added to the TF.
        """
        project = Project.objects.get(pk=user_profile.last_opened_project_id)
        ef = FinalFusion.objects.get(project=project)

        loaded_js = json.loads(self.content_json)
        columns = [{"name": "#", "ef_added": False}]

        for row in loaded_js:
            for i in row:
                obj = {
                    "name": i,
                    "ef_added": ef.tq_column_is_added(i, self)
                }

                if obj not in columns:
                    columns.append(obj)
        return {
            "cols": columns,
            "rows": loaded_js,
            "items": len(loaded_js)
        }

    def get_column(self, col_name):
        """
        :return All content from a specified column of this TQ.
        """
        loaded_js = json.loads(self.content_json)
        ret = []
        for row in loaded_js:
            ret.append(row[col_name])
        return ret

    def __str__(self):
        return "#%d: %s" % (self.pk, self.display_file_name)