"""
Webhook models.
"""
import uuid
from django.db import models
from django.utils.encoding import python_2_unicode_compatible


class ActiveManager(models.Manager):
    """
    Manager which returns only enabled webhooks.
    """
    def get_queryset(self, *args, **kwargs):
        """
        Returns only enabled webhooks.
        """
        # pylint: disable=super-on-old-class
        qs = super(ActiveManager, self).get_queryset(*args, **kwargs)
        return qs.filter(enabled=True)


@python_2_unicode_compatible
class Webhook(models.Model):
    """
    Represents possibly outgoing webhooks.
    """
    url = models.URLField()
    secret = models.CharField(max_length=32, default=lambda: uuid.uuid4().hex)
    enabled = models.BooleanField(default=True)

    objects = models.Manager()
    active = ActiveManager()

    def __str__(self):
        return self.url
