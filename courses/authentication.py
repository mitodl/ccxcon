"""
Provides key authentication capability to django-rest-framework.
"""
from django.conf import settings
from rest_framework import authentication, exceptions


class ValidUser(object):
    """
    Represents a valid user for login purposes.
    """

    def is_authenticated(self):  # pylint: disable=no-self-use
        """Always yes."""
        return True


class KeyAuthentication(authentication.BaseAuthentication):
    """
    Class which checks that incoming tokens match an allowed set of
    client keys. Allowed client keys are found in the
    CCXCON_ALLOWED_CLIENT_KEYS setting.
    """
    def authenticate(self, request):
        """
        Authenticates the user. returns (user, token), but we don't do
        users in CCXCon, so we only return the token.
        """
        if 'HTTP_AUTHORIZATION' not in request.META:
            return None

        auth = request.META['HTTP_AUTHORIZATION']
        if not auth:
            return None

        scheme, token = auth.split(" ")
        if scheme != "Token":
            return None

        if token not in settings.CCXCON_ALLOWED_CLIENT_KEYS:
            raise exceptions.AuthenticationFailed('Unknown token')

        return (ValidUser(), token)
