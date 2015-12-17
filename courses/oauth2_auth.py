"""
Overridden authentication mechanism which allows oauth2 applications
authenticating with client_credentials to be authenticated as the user of the
backing application.
"""
from oauth2_provider.ext.rest_framework import (
    OAuth2Authentication as BaseOAuth2Authentication,
)


class OAuth2Authentication(BaseOAuth2Authentication):
    """
    Authenticator that forces request.user to be present even if the
    oauth2_provider package doesn't want it to be.

    Works around the change introduced in:
    https://github.com/evonove/django-oauth-toolkit/commit/628f9e6ba98007d2940bb1a4c28136c03d81c245

    Reference:
    https://github.com/evonove/django-oauth-toolkit/issues/38

    """
    def authenticate(self, request):
        super_result = super(OAuth2Authentication, self).authenticate(request)

        if super_result:
            # The request was found to be authentic.
            user, token = super_result
            if user is None:
                user = token.application.user
                result = user, token
            else:
                result = super_result
            return result
