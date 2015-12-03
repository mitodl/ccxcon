"""
Signals for Course App
"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from courses.models import Course, Module
from webhooks.tasks import publish_webhook


@receiver(post_save, sender=Course)
@receiver(post_save, sender=Module)
# pylint: disable=unused-argument,protected-access
def publish_on_update(sender, instance, **kwargs):
    """
    Trigger publish when course or module saved.
    """
    publish_webhook.delay(
        '{}.{}'.format(instance._meta.app_label,
                       instance._meta.object_name),
        'uuid', instance.uuid)
