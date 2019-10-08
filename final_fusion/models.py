from django.db import models
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from project.models import Project


class FinalFusion(models.Model):
    """
    FinalFusion
    """
    creation_date = models.DateTimeField(default=timezone.now)
    name = models.CharField(max_length=40, default="Final Fusion")
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

    def get_col_vars(self):
        """
        get_col_vars
        """
        from final_fusion_column.models import FinalFusionColumn

        cv = {}
        ffc = FinalFusionColumn.objects.filter(final_fusion=self, archived=False).order_by("pk")
        for f in ffc:
            short_name = f.display_column_name[:3].upper()

            while short_name in cv:
                short_name += f.display_column_name[-1].upper()

            cv[short_name] = f.get_as_json()["name"]

        return cv



    def __str__(self):
        return "#%d: EF" % self.pk
