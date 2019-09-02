from django.db import models
from django.utils import timezone
from final_fusion.models import FinalFusion


class FinalFusionColumn(models.Model):
    """
    FinalFusionColumn
    """
    creation_date = models.DateTimeField(default=timezone.now)
    archived = models.BooleanField(default=False)
    final_fusion = models.ForeignKey(FinalFusion, on_delete=models.CASCADE)
    source_column_name = models.CharField(max_length=30)
    display_column_name = models.CharField(max_length=30)
    rows_json = models.TextField(max_length=2000)

    def __str__(self):
        return "#%d: %s" % (self.pk, self.display_column_name)
