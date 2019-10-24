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
    ignore_duplicates = models.BooleanField(default=False)

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

    @staticmethod
    def count_duplicates(user_profile):
        """
        count_duplicates
        """
        import final_fusion.views as ff_v

        count = 0
        table = ff_v.get_preview_table(user_profile)
        checked_rows = []

        for row in table["out_rows"]:
            vals = list(row.values())
            if vals in checked_rows:
                count += 1

            checked_rows.append(vals)

        return count

    @staticmethod
    def remove_duplicates(rows):
        """
        remove_duplicates
        """
        checked_rows = []
        indices = []

        for row in rows:
            vals = list(row.values())
            if vals in checked_rows:
                indices.append(rows.index(row))

            checked_rows.append(vals)

        for i in indices:
            rows.remove(rows[i])

        return rows

    def __str__(self):
        return "#%d: %s" % (self.pk, self.name)
