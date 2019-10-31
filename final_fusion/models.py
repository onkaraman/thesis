from django.db import models
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from project.models import Project


class FinalFusion(models.Model):
    """
    This model contains minimal data, but serves as a binding element among other
    models to represent a final fusion OR a "Teilfusion", meaning a final fusion
    in progress.
    """
    creation_date = models.DateTimeField(default=timezone.now)
    name = models.CharField(max_length=40, default="Final Fusion")
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    ignore_duplicates = models.BooleanField(default=False)

    def tq_column_is_added(self, name, tq):
        """
        Will return True if a specified column of a TQ is already part of this fusion.
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
        Used for scripting rule modules. Will return a dictionary of columns of a row with shortened names.
        Will also provide additional sum and average columns of each column containing only numeric content.
        """
        from final_fusion_column.models import FinalFusionColumn

        cv = {}
        ffc = FinalFusionColumn.objects.filter(final_fusion=self, archived=False).order_by("pk")
        for f in ffc:
            short_name = f.display_column_name[:3].upper()

            while short_name in cv:
                short_name += f.display_column_name[-1].upper()

            cv[short_name] = f.get_as_json()["name"]

            if f.has_numeric_content():
                rows = f.get_rows_as_list()
                if sum(rows) > 0:
                    cv["%s.SUM" % short_name] = sum(rows)
                    cv["%s.AVG" % short_name] = int(sum(rows)/len(rows))

        return cv

    @staticmethod
    def count_duplicates(user_profile):
        """
        Will return the count of row-duplicates. A row-duplicate is a row, which is already part of the fusion
        with all single column elements already present.
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
        Will first go through all rows to find the duplicates by their row-indices. Will then
        remove the (duplicate) items of the passed row parameter by their indicides.
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
