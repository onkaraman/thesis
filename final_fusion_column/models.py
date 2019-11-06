import json
from django.db import models
from django.utils import timezone
from final_fusion.models import FinalFusion
from tq_file.models import TQFile
from rule_module.models import RuleModule


class FinalFusionColumn(models.Model):
    """
    An object of this model will be created, when a column of a TQ will be selected for inclusion
    into the TF. A single object of this class contains only row data of selected column.
    FFC objects in composition form a TF/EF.
    """
    creation_date = models.DateTimeField(default=timezone.now)
    archived = models.BooleanField(default=False)
    final_fusion = models.ForeignKey(FinalFusion, on_delete=models.CASCADE)
    source_tq = models.ForeignKey(TQFile, on_delete=models.CASCADE, null=True)
    source_column_name = models.CharField(max_length=30)
    display_column_name = models.CharField(max_length=30)
    rows_json = models.TextField(max_length=2000)
    rm_dependency = models.ForeignKey(RuleModule, on_delete=models.CASCADE, null=True)
    manually_removable = models.BooleanField(default=False)

    def get_as_json(self):
        """
        Will return key information of this FFC in JSON-Form.
        """
        if self.source_tq:
            name = "%s (%s)" % (self.display_column_name, self.source_tq.display_file_name)
        else:
            name = self.display_column_name

        return {
            "pure_name": self.display_column_name,
            "name": name,
            "dynamic": self.source_tq is None,
            "rows": self.rows_json
        }

    def has_numeric_content(self):
        """
        :return: True if all rows on this column are numeric.
        """
        for r in json.loads(self.rows_json):
            if not str(r).isdigit():
                return False
        return True

    def get_rows_as_list(self):
        """
        :return: Will return list containing all row items.
        """
        return [i for i in json.loads(self.rows_json)]

    def __str__(self):
        if self.source_tq:
            return "#%d: %s (TQ %s)" % (self.pk, self.display_column_name, self.source_tq.pk)
        else:
            return "#%d: %s" % (self.pk, self.display_column_name)
