"""
Test for custom django-rest-framework authentication class.
"""
# pylint: disable=no-self-use
from datetime import timedelta

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from django.test import TestCase, RequestFactory

from oauth2_provider.models import Application, AccessToken

from .oauth2_auth import OAuth2Authentication


class OAuth2AuthenticationTests(TestCase):
    """
    Tests for OAuth2Authentication
    """
    def test_returns_proper_user_on_request_object(self):
        """
        Returns proper user on request object.
        """
        user = User.objects.create_user('test')
        req_factory = RequestFactory()
        app = Application.objects.create(name='test app', user=user)
        token = AccessToken.objects.create(
            token='test-token',
            application=app,
            expires=timezone.now() + timedelta(days=1))
        request = req_factory.get(reverse('course-list'), **{
            'HTTP_AUTHORIZATION': 'Bearer {}'.format(token.token),
        })
        subject = OAuth2Authentication()

        result = subject.authenticate(request)

        assert result, "Expected request to be a valid authentication call"
        assert result[0] == user, "Expected user to be the oauth app's user"
