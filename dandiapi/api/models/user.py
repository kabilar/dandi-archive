from __future__ import annotations

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db import models
from django_extensions.db.models import TimeStampedModel


class UserMetadata(TimeStampedModel):
    class Status(models.TextChoices):
        INCOMPLETE = 'INCOMPLETE'
        PENDING = 'PENDING'
        APPROVED = 'APPROVED'
        REJECTED = 'REJECTED'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='metadata')
    status = models.CharField(choices=Status.choices, default=Status.INCOMPLETE, max_length=10)
    questionnaire_form = models.JSONField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, default='', max_length=1000)
    webknossos_credential = models.CharField(max_length=128, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Ensure the password is hashed before saving if it is not null or empty
        if self.password and not self.password.startswith('pbkdf2_sha256'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

