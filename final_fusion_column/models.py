from django.db import models
from django.utils import timezone
from final_fusion.models import FinalFusion
from tq_file.models import TQFile
from rule_module.models import RuleModule


class FinalFusionColumn(models.Model):
    """
    FinalFusionColumn
    """
    creation_date = models.DateTimeField(default=timezone.now)
    archived = models.BooleanField(default=False)
    final_fusion = models.ForeignKey(FinalFusion, on_delete=models.CASCADE)
    source_tq = models.ForeignKey(TQFile, on_delete=models.CASCADE, null=True)
    source_column_name = models.CharField(max_length=30)
    display_column_name = models.CharField(max_length=30)
    rows_json = models.TextField(max_length=2000)
    rm_dependency = models.ForeignKey(RuleModule, on_delete=models.CASCADE, null=True)

    def get_as_json(self):
        """
        get_as_json
        """
        if self.source_tq:
            source_name = self.source_tq.display_file_name
        else:
            source_name = "DYN"

        return {
            "name": "%s (%s)" % (self.display_column_name, source_name),
            "rows": self.rows_json
        }

    def __str__(self):
        return "#%d: %s" % (self.pk, self.display_column_name)
