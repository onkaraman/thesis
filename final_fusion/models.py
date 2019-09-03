from django.db import models
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from project.models import Project


class FinalFusion(models.Model):
    """
    FinalFusion
    """
    creation_date = models.DateTimeField(default=timezone.now)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def tq_column_is_added(self, name, tq):
        """
        tq_column_is_added
        """
        from final_fusion_column.models import FinalFusionColumn
        try:
            FinalFusionColumn.objects.get(final_fusion=self,
                                          source_tq=tq,
                                          source_column_name=name,
                                          archived=False)
            return True
        except ObjectDoesNotExist:
            return False

    def __str__(self):
        return "#%d: EF" % self.pk
