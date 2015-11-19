"""
Test driver for Dredd
"""
import os
from six.moves import urllib_parse as urlparse
import subprocess

from django.conf import settings
from django.test import LiveServerTestCase


class DreddTestCase(LiveServerTestCase):
    """Tests Dredd related tests."""
    def test_dredd(self):
        """
        Run test via Dredd.

        We need to muck with the database url, among other things, to setup the
        environment for testing properly, since we need to inform the dredd
        script about our db config.
        """
        args = [
            "dredd",
            "{}/apiary.apib".format(settings.BASE_DIR),
            self.live_server_url,
            "-f", "apiary_hooks.py",
            "--language", "python",
        ]
        old_url = urlparse.urlparse(os.getenv('DATABASE_URL'))
        new_url = old_url._replace(
            path=old_url.path.replace('/postgres', '/test_postgres')).geturl()

        call = subprocess.Popen(
            args,
            env=dict(os.environ, **{
                "PYTHONPATH": settings.BASE_DIR,
                "DATABASE_URL": new_url,
                }))
        call.wait()
        self.assertEqual(0, call.returncode, call.stdout)
