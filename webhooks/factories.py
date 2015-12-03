"""Factories for testing"""
from factory.django import DjangoModelFactory
from .models import Webhook


class WebhookFactory(DjangoModelFactory):
    """Factory for Webhook"""
    class Meta:  # pylint: disable=missing-docstring
        model = Webhook
