"""
Celery tests.
"""
# pylint: disable=no-self-use
import hashlib
import hmac
import json
import mock

from django.contrib.auth.models import User
from django.core.exceptions import FieldError
from django.test import TestCase
from django.utils.crypto import constant_time_compare
from django.utils.encoding import force_bytes
import pytest
from requests.exceptions import RequestException

from courses.factories import CourseFactory
from webhooks.factories import WebhookFactory
from webhooks.tasks import publish_webhook


class PublishWebhookTests(TestCase):
    """
    Tests for webhook publishing.
    """
    def test_model_getting_catches_error(self):
        """
        Should catch error if invalid model to import.
        """
        with pytest.raises(LookupError):
            publish_webhook('foo.Bar', 'pk', 1)

    def test_malformed_model_str_throws_error(self):
        """
        Should catch error if invalid model to import.
        """
        with pytest.raises(ValueError):
            publish_webhook('foo.Bar.Zot', 'pk', 1)

    def test_model_posts_to_endpoint(self):
        """
        Happy case of posting.
        """
        WebhookFactory.create(url="http://example.org")
        course = CourseFactory.create()
        with mock.patch('webhooks.tasks.requests', autospec=True) as mock_requests:
            publish_webhook('courses.Course', 'pk', course.pk)
            assert mock_requests.post.call_count == 1
            _, kwargs = mock_requests.post.call_args
            payload = kwargs['json']
            assert isinstance(payload, dict)
            assert payload['action'] == 'update'

    def test_no_post_if_no_webhook_method(self):
        """
        If there's no to_webhook method, don't attempt to serialize.
        """
        WebhookFactory.create(url="http://example.org")
        user = User.objects.create()
        with mock.patch('webhooks.tasks.requests', autospec=True) as mock_requests:
            publish_webhook('auth.User', 'pk', user.pk)
            assert mock_requests.post.call_count == 0

    def test_no_model_sends_delete(self):
        """
        If there's no model, send a delete.
        """
        WebhookFactory.create(url="http://example.org")
        with mock.patch('webhooks.tasks.requests', autospec=True) as mock_requests:
            publish_webhook('courses.Course', 'pk', 1)
            assert mock_requests.post.call_count == 1
            _, kwargs = mock_requests.post.call_args
            assert kwargs['json']['action'] == 'delete'

    def test_secure_header_verification(self):
        """
        Verifies that we sign each webhook request.
        """
        wh = WebhookFactory.create(url="http://example.org")
        course = CourseFactory.create()
        with mock.patch('webhooks.tasks.requests', autospec=True) as mock_requests:
            publish_webhook('courses.Course', 'pk', course.pk)
            assert mock_requests.post.call_count == 1
            _, kwargs = mock_requests.post.call_args
            assert kwargs['json']['action'] == 'update'

            # This constant_time_compare is important for implementations to
            # ensure they're not vulnerable to timing attacks.
            assert constant_time_compare(
                kwargs['headers']['X-CCXCon-Signature'], hmac.new(
                    force_bytes(wh.secret), force_bytes(json.dumps(kwargs['json'])),
                    hashlib.sha1).hexdigest())

    def test_one_post_of_many_failing(self):
        """
        Validates that if one post fails they don't all fail.
        """
        WebhookFactory.create(url="http://example.org")
        WebhookFactory.create(url="http://example.com")
        course = CourseFactory.create()
        with mock.patch('webhooks.tasks.requests', autospec=True) as mock_requests:
            mock_requests.post.side_effect = [RequestException("couldn't post"), None]
            publish_webhook('courses.Course', 'pk', course.pk)
            assert mock_requests.post.call_count == 2

    def test_lookup_by_non_pk(self):
        """
        Should be able to look things up by uuid too.
        """
        WebhookFactory.create(url="http://example.org")
        course = CourseFactory.create()
        with mock.patch('webhooks.tasks.requests', autospec=True) as mock_requests:
            publish_webhook('courses.Course', 'uuid', course.uuid)
            assert mock_requests.post.call_count == 1

    def test_lookup_by_nonexistent_field(self):
        """
        Properly handles error if non-existent field provided.
        """
        WebhookFactory.create(url="http://example.org")
        course = CourseFactory.create()
        with mock.patch('webhooks.tasks.requests', autospec=True):
            with pytest.raises(FieldError):
                publish_webhook('courses.Course', 'asdf', course.pk)
