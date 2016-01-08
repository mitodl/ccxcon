"""
Util tests.
"""
# pylint: disable=no-self-use,unused-argument
from datetime import timedelta
import json
import mock

from django.test import TestCase
from django.utils.timezone import now

import pytest

from .factories import BackingInstanceFactory, PrefetchBackingInstanceFactory
from .models import BackingInstance
from .utils import get_access_token, UnretrievableToken


class GetAccessTokenTests(TestCase):
    """
    Tests for get_access_token
    """
    def test_current_token_returns(self):
        """
        If the token is current, return it.
        """
        bi = BackingInstanceFactory.create(
            instance_url='http://valid',
            access_token='asdf',
            access_token_expiration=now() + timedelta(days=1))

        result = get_access_token(bi)

        assert result == 'asdf'

    def test_fetch_errors_throws_exception(self):
        """
        If the access token fetch returns non-200, throw exception.
        """
        bi = PrefetchBackingInstanceFactory.create(
            instance_url='http://no_access',
            grant_token='qwerty')
        assert bi.is_expired

        with mock.patch('oauth_mgmt.utils.requests', autospec=True) as m_req:
            m_req.post.return_value.status_code = 500
            with pytest.raises(UnretrievableToken):
                get_access_token(bi)

    def test_grant_fetch_updates_db(self):
        """
        Info saved to db on grant fetch.
        """
        bi = PrefetchBackingInstanceFactory.create(
            instance_url='http://no_access',
            grant_token='qwerty')
        payload = {
            "access_token": "cbd1ea3d162a265b186fabea378c68b603c5c96e",
            "token_type": "Bearer",
            "expires_in": 31535999,
            "refresh_token": "82592b794640452074678d2dd9e9136bd01e03a1",
            "scope": ""
        }

        with mock.patch('oauth_mgmt.utils.requests', autospec=True) as m_req:
            m_req.post.return_value.content = json.dumps(payload)
            m_req.post.return_value.json = lambda: json.loads(m_req.post.return_value.content)
            m_req.post.return_value.status_code = 200

            result = get_access_token(bi)

            _, kwargs = m_req.post.call_args
            assert kwargs['data']['grant_type'] == 'authorization_code'

        instance = BackingInstance.objects.get(pk=bi.id)

        assert result == payload['access_token']
        assert instance.access_token == payload['access_token']
        assert instance.refresh_token == payload['refresh_token']
        # Assert refresh token is in the far future, giving ample room for
        # difference between timezone.now in method under test and our call.
        assert instance.access_token_expiration >= now() + \
            timedelta(seconds=payload['expires_in']) - timedelta(hours=1)

    def test_refresh_fetch_updates_db(self):
        """
        Persist info if refreshing token
        """
        bi = BackingInstanceFactory.create(
            instance_url='http://valid',
            grant_token='qwerty',
            access_token='asdf',
            access_token_expiration=now() - timedelta(days=3),
            refresh_token='jkll',
        )
        payload = {
            "access_token": "c98f5775ef4ddda409b45ae1f1823c0968f67573",
            "token_type": "Bearer",
            "expires_in": 31535999,
            "refresh_token": "72a21ef20bf623fe8876f1714d55f4633f5803e5",
            "scope": ""
        }

        with mock.patch('oauth_mgmt.utils.requests.post', autospec=True) as m_post:
            m_post.return_value.status_code = 200
            m_post.return_value.json = lambda: payload
            m_post.return_value.content = json.dumps(payload)

            result = get_access_token(bi)

            _, kwargs = m_post.call_args
            assert kwargs['data']['grant_type'] == 'refresh_token'

        instance = BackingInstance.objects.get(id=bi.id)
        assert result == payload['access_token']
        assert instance.access_token == payload['access_token']
        assert instance.refresh_token == payload['refresh_token']
        # -1hr is to account for room between now() invocations.
        assert instance.access_token_expiration >= now() + \
            timedelta(seconds=payload['expires_in']) - timedelta(hours=1)
