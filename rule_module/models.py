from django.db import models
from django.utils import timezone
from final_fusion.models import FinalFusion


class RuleModule(models.Model):
    """
    RuleModule
    """
    creation_date = models.DateTimeField(default=timezone.now)
    archived = models.BooleanField(default=False)
    name = models.CharField(max_length=100)
    final_fusion = models.ForeignKey(FinalFusion, on_delete=models.CASCADE)

    rule_type = models.CharField(max_length=10)
    subjects = models.CharField(max_length=200, null=True)
    if_conditions = models.CharField(max_length=200)
    then_cases = models.CharField(max_length=200)

    def __str__(self):
        return "#%d: (%s) Rule: %s" % (self.pk, self.rule_type, self.name)
