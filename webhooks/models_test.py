"""
Model tests
"""
# pylint: disable=no-self-use
from django.test import TestCase

from webhooks.models import Webhook, get_uuid_hex
from webhooks.factories import WebhookFactory


class ActiveManagerTests(TestCase):
    """
    Tests for ActiveManager
    """
    def test_excludes_disabled(self):
        """Excludes disabled webhooks"""
        WebhookFactory.create(enabled=True)
        wh = WebhookFactory.create(enabled=False)
        qs = Webhook.active.all()
        assert qs.count() == 1
        assert wh not in qs

    def test_includes_enabled(self):
        """Includes enabled webhooks"""
        wh = WebhookFactory.create(enabled=True)
        WebhookFactory.create(enabled=False)
        qs = Webhook.active.all()
        assert qs.count() == 1
        assert wh in qs


class WebhookModelTests(TestCase):
    """
    Webhook Model Tests
    """
    def test_to_string(self):
        """
        Test __str__ method returns url
        """
        url = "https://google.com"
        webhook = WebhookFactory.build(url=url)
        self.assertEqual(url, "{}".format(webhook))
        self.assertEqual(str, type(webhook.__str__()))

    def test_uuid_helper(self):
        """
        Test UUID helper returns something that looks like a uuid and is
        somewhat random.
        """
        assert len(get_uuid_hex()) == 32
        assert get_uuid_hex() != get_uuid_hex()
