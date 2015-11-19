"""Tests regarding REST API"""
import json

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase

from courses.factories import CourseFactory, ModuleFactory


class ApiTests(TestCase):
    """Tests regarding REST API"""
    @staticmethod
    def _correct_auth_header():
        """Returns a correct auth header for valid requests"""
        return "Token {}".format(settings.CCXCON_ALLOWED_CLIENT_KEYS.copy().pop())

    def test_login_required(self):
        """Returns 403 errors if we didn't pass in a login header."""
        m1 = ModuleFactory.create()
        resp = self.client.get(reverse('module-list', args=(m1.course.uuid,)))
        self.assertEqual(403, resp.status_code)

    def test_invalid_login_prevented(self):
        """Returns 403 errors if we didn't pass in a known auth key."""
        m1 = ModuleFactory.create()
        resp = self.client.get(reverse('module-list', args=(m1.course.uuid,)),
                               HTTP_AUTHORIZATION="Token asdf")
        self.assertEqual(403, resp.status_code)

    def test_invalid_login__unknown_scheme(self):
        """Returns 403 errors if we didn't pass in a known scheme."""
        m1 = ModuleFactory.create()
        resp = self.client.get(reverse('module-list', args=(m1.course.uuid,)),
                               HTTP_AUTHORIZATION="Basic asdf")
        self.assertEqual(403, resp.status_code)

    def test_valid_login(self):
        """Returns 200 errors if we did everything correctly."""
        m1 = ModuleFactory.create()
        resp = self.client.get(reverse('module-list', args=(m1.course.uuid,)),
                               HTTP_AUTHORIZATION=ApiTests._correct_auth_header())
        self.assertEqual(200, resp.status_code)

    def test_separate_children(self):
        """
        Test that a course's modules list endpoint doesn't contain modules
        from other courses.
        """
        m1 = ModuleFactory.create()
        m2 = ModuleFactory.create()

        # Different courses
        self.assertNotEqual(m1.course, m2.course)

        resp = self.client.get(reverse('module-list', args=(m1.course.uuid,)),
                               HTTP_AUTHORIZATION=ApiTests._correct_auth_header())
        payload = json.loads(resp.content.decode('utf-8'))
        self.assertEqual(len(payload), 1)

    def test_bad_json(self):
        """
        Test that invalid JSON is rejected and model state is unaffected.
        """
        course = CourseFactory.create(**{
            "title": "title1",
            "author_name": "author1",
            "overview": "overview1",
            "description": "description1",
            "video_url": "http://youtube.com/1",
            "edx_instance": "edx1",
            "price_per_seat_cents": 1,
        })

        module_dict = {
            "title": "title",
            "subchapters": "['a', 3]",
            "price_per_seat_cents": 3
        }
        modules_url = reverse('module-list', args=(course.uuid,))
        resp = self.client.post(modules_url, module_dict,
                                HTTP_AUTHORIZATION=ApiTests._correct_auth_header())
        self.assertEqual(resp.status_code, 400)  # Invalid JSON

        resp = self.client.get(modules_url,
                               HTTP_AUTHORIZATION=ApiTests._correct_auth_header())
        self.assertEqual(resp.status_code, 200, resp.content)
