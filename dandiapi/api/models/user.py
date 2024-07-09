from __future__ import annotations

import os

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db import models, transaction
from django_extensions.db.models import TimeStampedModel
from django.utils.crypto import get_random_string



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
        with transaction.atomic():

            # Register user for WebKNOSSOS if not yet registered
            # if not self.webknossos_credential and os.getenv('WEBKNOSSOS_API_URL', None):
            random_password = get_random_string(length=12)
            self.webknossos_credential = random_password

            # Offset to celery task to call /register in WebKNOSSOS
            from dandiapi.api.tasks import register_post_external_api_task

            webknossos_api_url = os.getenv('WEBKNOSSOS_API_URL')
            register_post_external_api_task.delay(
                external_endpoint='https://webknossos-staging.lincbrain.org/api/auth/register',
                post_payload={
                "firstName": self.user.first_name,
                "lastName": self.user.last_name,
                "email": self.user.email,
                "organization": "LINC_Staging",
                "organizationDisplayName": "LINC Staging",
                "password": {
                    "password1": self.webknossos_credential,
                    "password2": self.webknossos_credential
                }
            })

        super().save(*args, **kwargs)

