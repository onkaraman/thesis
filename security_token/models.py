import uuid
import random
from datetime import datetime
from django.db import models
from django.utils import timezone
from django.utils.timezone import utc
from django.db.models import signals


class SecurityToken(models.Model):
    creation_date = models.DateTimeField(default=timezone.now)
    code = models.CharField(max_length=60)
    expiration_after_days = models.IntegerField(default=14)

    def has_expired(self):
        timediff = datetime.utcnow().replace(tzinfo=utc) - self.creation_date
        return timediff.days > self.expiration_after_days

    def generate_token_code(self):
        self.code = str(uuid.uuid4()) + str(random.randint(0, 1000))
        return self.code


def security_token_pre_save(sender, instance, **kwargs):
    if len(instance.code) <= 20:
        raise ValueError("Security code is too short.")
    if not any(char.isdigit() for char in instance.code):
        raise ValueError("Security code doesn't contain any numbers")
    if instance.expiration_after_days <= 0:
        raise ValueError("Expiration after days must be at least 1")


signals.pre_save.connect(security_token_pre_save, sender=SecurityToken)
