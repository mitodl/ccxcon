"""
Model Factories
"""
from datetime import timedelta, datetime
from django.utils.timezone import now, make_aware
import factory
from factory.django import DjangoModelFactory

from .models import BackingInstance


class BackingInstanceFactory(DjangoModelFactory):
    """Factory for BackingInstance"""
    instance_url = factory.Sequence("https://edx-{}.org".format)
    access_token = 'test-token-here'
    access_token_expiration = factory.LazyAttribute(lambda x: now() + timedelta(hours=5))

    class Meta:  # pylint: disable=missing-docstring
        model = BackingInstance


class PrefetchBackingInstanceFactory(BackingInstanceFactory):
    """
    BackingInstance before fetching the grant.
    """
    access_token = None
    access_token_expiration = make_aware(datetime(1970, 1, 1, 0, 0))
