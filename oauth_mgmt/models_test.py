"""
Model tests.
"""
from datetime import timedelta
from django.utils.timezone import now
import pytest
from .models import BackingInstance


def test_backing_instance_str():
    "__str__ returns url"
    assert str(BackingInstance(instance_url='https://edx.org')) == "https://edx.org"


@pytest.mark.parametrize("incoming,expected", [
    (now(), True),
    (now() - timedelta(days=1), True),
    (now() + timedelta(hours=1), True),  # no padding
    (now() + timedelta(hours=3), False),
    (now() + timedelta(days=1), False),
    (None, True),  # null
])
def test_expiration(incoming, expected):
    """Validate expiration tests correct conditions"""
    assert BackingInstance(access_token_expiration=incoming).is_expired == expected
