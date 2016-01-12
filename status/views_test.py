"""
Tests for the views module
"""

import json
from copy import deepcopy

import mock
import redis
from django.conf import settings
from django.core.urlresolvers import reverse
# from django.test import Client
from django.test.testcases import TestCase
from rest_framework import status as status_codes

from status import views


class TestStatus(TestCase):
    """Test output of status page."""

    def setUp(self):
        super(TestStatus, self).setUp()
        # Create test client.
        self.url = reverse("status")
        # Save some settings to restore them at the end of the test
        self.broker_url = settings.BROKER_URL
        self.databases = settings.DATABASES

    def tearDown(self):
        super(TestStatus, self).tearDown()
        # restore configuration in settings
        settings.BROKER_URL = self.broker_url
        settings.DATABASES = self.databases

    def get(self, expected_status=status_codes.HTTP_200_OK, token=settings.STATUS_TOKEN):
        """
        Helper method to perform GET requests
        """
        if token is None:
            resp = self.client.get(self.url)
        else:
            resp = self.client.get(self.url, data={"token": token})
        self.assertEqual(resp.status_code, expected_status)
        return json.loads(resp.content.decode('utf-8'))

    def test_token(self):
        """
        Caller must have correct token.
        """
        # No token.
        resp = self.get(status_codes.HTTP_400_BAD_REQUEST, token=None)
        self.assertIn("error", resp)
        self.assertEqual(resp["error"], "token_error")

        # Invalid token.
        resp = self.get(status_codes.HTTP_400_BAD_REQUEST, "wrong_token")
        self.assertIn("error", resp)
        self.assertEqual(resp["error"], "token_error")

    def test_status(self):
        """
        Get normally.
        """
        # mocking the celery call because celery may be unavailable during tests
        with mock.patch('celery.task.control.inspect', autospec=True) as mocked:
            # just checking that there is a response from celery
            mocked.return_value.stats.return_value = {'foo': 'bar'}
            resp = self.get()
        for key in ("postgresql", "redis", "celery"):
            self.assertIn(key, resp)
            self.assertIn("status", resp[key])
            self.assertEqual(resp[key]["status"], views.UP)

    def test_no_configuration(self):
        """
        Test for configuration missing for redis and postgres.
        """
        del settings.BROKER_URL
        del settings.DATABASES
        with mock.patch('celery.task.control.inspect', autospec=True) as mocked:
            mocked.return_value.stats.return_value = {'foo': 'bar'}
            resp = self.get()
        # ignoring celery
        for key in ("postgresql", "redis"):
            self.assertIn(key, resp)
            self.assertIn("status", resp[key])
            self.assertEqual(resp[key]["status"], views.NO_CONFIG)

    def test_wrong_settings(self):
        """
        Test for wrong settings for redis and postgres.
        """
        wrong_setting = " wrong setting "
        broker_url = wrong_setting
        databases = deepcopy(settings.DATABASES)
        databases['default'] = wrong_setting
        with self.settings(BROKER_URL=broker_url, DATABASES=databases):
            with mock.patch('celery.task.control.inspect', autospec=True) as mocked:
                mocked.return_value.stats.return_value = {'foo': 'bar'}
                resp = self.get(status_codes.HTTP_503_SERVICE_UNAVAILABLE)
        # ignoring celery
        for key in ("postgresql", "redis"):
            self.assertIn(key, resp)
            self.assertIn("status", resp[key])
            self.assertEqual(resp[key]["status"], views.DOWN)

    def test_wrong_configuration(self):
        """
        Test for wrong configuration for redis and postgres.
        """
        broker_url = "redis://foobar:6379/4"
        databases = deepcopy(settings.DATABASES)
        databases["default"]["HOST"] = "foobar"
        with self.settings(BROKER_URL=broker_url, DATABASES=databases):
            with mock.patch('celery.task.control.inspect', autospec=True) as mocked:
                mocked.return_value.stats.return_value = {'foo': 'bar'}
                resp = self.get(status_codes.HTTP_503_SERVICE_UNAVAILABLE)
        # ignoring celery
        for key in ("postgresql", "redis"):
            self.assertIn(key, resp)
            self.assertIn("status", resp[key])
            self.assertEqual(resp[key]["status"], views.DOWN)

    def test_redis_response_error(self):
        """
        Specific test when redis raises a RedisResponseError
        """
        with mock.patch('celery.task.control.inspect', autospec=True) as mocked:
            mocked.return_value.stats.return_value = {'foo': 'bar'}
            with mock.patch('redis.StrictRedis', autospec=True) as mocked_redis:
                mocked_redis.return_value.info.side_effect = redis.ResponseError()
                resp = self.get(status_codes.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn("redis", resp)
        self.assertIn("status", resp["redis"])
        self.assertEqual(resp["redis"]["status"], views.DOWN)

    def test_celery_errors(self):
        """
        Specific test for celery errors
        """
        # no answer in the stats call
        with mock.patch('celery.task.control.inspect', autospec=True) as mocked:
            mocked.return_value.stats.return_value = {}
            resp = self.get(status_codes.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn("celery", resp)
        self.assertIn("status", resp["celery"])
        self.assertEqual(resp["celery"]["status"], views.DOWN)

        # exception in the stats call
        with mock.patch('celery.task.control.inspect', autospec=True) as mocked:
            mocked.side_effect = IOError()
            resp = self.get(status_codes.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn("celery", resp)
        self.assertIn("status", resp["celery"])
        self.assertEqual(resp["celery"]["status"], views.DOWN)
