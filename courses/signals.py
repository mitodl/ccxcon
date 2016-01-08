"""
Signals for Course App
"""
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from courses.models import Course, Module, UserInfo
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
        'uuid', str(instance.uuid))


@receiver(post_save, sender=User)
# pylint: disable=unused-argument
def create_info_object(sender, instance, created, **kwargs):
    """
    Ensure there is a UserInfo object for every user.
    """
    if created and not hasattr(instance, 'info'):
        UserInfo.objects.create(user=instance)
