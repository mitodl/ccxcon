"""
Models for managing OAuth things.
"""
from __future__ import unicode_literals
from datetime import datetime, timedelta

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import make_aware, now


@python_2_unicode_compatible
class BackingInstance(models.Model):
    """
    Represents OAuth things for the backing instance of EdX.
    """
    instance_url = models.URLField(max_length=255, unique=True)
    oauth_client_id = models.CharField(max_length=128, blank=True, null=True)
    oauth_client_secret = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(
        max_length=30, blank=True, null=True,
        help_text="Username the backing oauth user is attached to. This is used to request course "
        "structure and MUST be a staff member of the course.")
    grant_token = models.CharField(max_length=128, blank=True, null=True)
    refresh_token = models.CharField(max_length=128, null=True, blank=True)
    access_token = models.CharField(max_length=128, null=True, blank=True)
    access_token_expiration = models.DateTimeField(default=make_aware(datetime(1970, 1, 1)))

    def __str__(self):
        return self.instance_url

    @property
    def is_expired(self):
        """
        Returns whether the access token is expired
        """
        if not self.access_token_expiration:  # pre-persistence
            return True
        return self.access_token_expiration <= now() + timedelta(hours=2)
