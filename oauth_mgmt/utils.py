"""
Utility functions.
"""
from datetime import timedelta
from six.moves.urllib.parse import urljoin  # pylint: disable=import-error

from six.moves.urllib.parse import urljoin  # pylint: disable=import-error
from django.utils.timezone import now
import requests


class UnretrievableToken(Exception):
    """
    Exception thrown when we can't fetch an access token.
    """


def get_access_token(instance):
    """
    Fetch a usable access token.

    Args:
        instance (oauth_mgmt.models.BackingInstance): OAuth2 app to get tokens for

    Returns:
        access_token (str): The bearer token to use as the value in the Authorization header.
    """
    if not instance.is_expired:
        # Return currently valid token.
        return instance.access_token
    elif not instance.access_token:
        # Get an access token.
        params = {
            "grant_type": "authorization_code",
            "response_type": "code",
            "client_id": instance.oauth_client_id,
            "client_secret": instance.oauth_client_secret,
            "code": instance.grant_token,
        }

    else:
        # refresh the token
        params = {
            "grant_type": "refresh_token",
            "client_id": instance.oauth_client_id,
            "client_secret": instance.oauth_client_secret,
            "refresh_token": instance.refresh_token,
        }

    resp = requests.post(
        urljoin(instance.instance_url, '/oauth2/access_token/'),
        data=params)
    if resp.status_code >= 300:
        raise UnretrievableToken(
            "Could not request token: Status: {status}, Message: {msg}".format(
                status=resp.status_code,
                msg=resp.content,
            ))

    j_resp = resp.json()
    instance.access_token = j_resp['access_token']
    instance.refresh_token = j_resp['refresh_token']
    instance.access_token_expiration = now() + timedelta(seconds=j_resp['expires_in'])
    instance.save()

    return instance.access_token
