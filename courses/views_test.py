"""Tests regarding REST API"""
import json
import uuid

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from courses.factories import CourseFactory, ModuleFactory, EdxAuthorFactory
from courses.models import EdxAuthor, Course


class ApiTests(TestCase):
    """Tests regarding REST API"""
    def setUp(self):
        self.user = User.objects.create_user('test', password='test')
        self.user.info.edx_instance = 'https://edx.org'
        self.user.info.save()
        assert self.client.login(username='test', password='test')


class JsonResponseTests(ApiTests):
    """
    Tests that json responses are what we expect.
    """
    def test_separate_children(self):
        """
        Test that a course's modules list endpoint doesn't contain modules
        from other courses.
        """
        m1 = ModuleFactory.create()
        m2 = ModuleFactory.create()

        # Different courses
        self.assertNotEqual(m1.course, m2.course)

        resp = self.client.get(reverse('module-list', args=(m1.course.uuid,)))
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
            "image_url": "http://placehold.it/350x150",
            "edx_instance": "edx1",
        })

        module_dict = {
            "title": "title",
            "subchapters": "['a', 3]",
        }
        modules_url = reverse('module-list', args=(course.uuid,))
        resp = self.client.post(modules_url, module_dict)
        self.assertEqual(resp.status_code, 400)  # Invalid JSON

        resp = self.client.get(modules_url)
        self.assertEqual(resp.status_code, 200, msg=resp.content)

    def test_create_course_accepts_instructors(self):
        """
        Validate course create endpoint accepts instructors
        """
        resp = self.client.post(reverse('course-list'), {
            "title": "title1",
            "author_name": "author1",
            "overview": "overview1",
            "description": "description1",
            "image_url": "http://placehold.it/350x150",
            "edx_instance": "http://edx.org/",
            "instructors": [
                "861e87a0803e436b989cb62d5e672c5f",
                "961e87a0803e436b989cb62d5e672c5f"
            ]
        })
        self.assertEqual(resp.status_code, 201, msg=resp.content)
        assert EdxAuthor.objects.count() == 2

    def test_edx_instance_applied_automatically(self):
        """
        edx_instance applied automatically.
        """
        resp = self.client.post(reverse('course-list'), {
            "title": "title1",
            "author_name": "author1",
            "overview": "overview1",
            "description": "description1",
            "image_url": "http://youtube.com/1",
            "edx_instance": "",
            "instructors": [
                "861e87a0803e436b989cb62d5e672c5f",
                "961e87a0803e436b989cb62d5e672c5f"
            ]
        })
        self.assertEqual(resp.status_code, 201, msg=resp.content)
        assert Course.objects.all()[0].edx_instance == 'https://edx.org'

    def test_requires_edx_instance(self):
        """
        If no edx_instance available, throw error
        """
        User.objects.create_user('no-instance', password='test')
        assert self.client.login(username='no-instance', password='test')
        resp = self.client.post(reverse('course-list'), {
            "title": "title1",
            "author_name": "author1",
            "overview": "overview1",
            "description": "description1",
            "image_url": "http://youtube.com/1",
            "edx_instance": "",
            "instructors": [
                "861e87a0803e436b989cb62d5e672c5f",
                "961e87a0803e436b989cb62d5e672c5f"
            ]
        })
        self.assertEqual(resp.status_code, 400, resp.content)


class UserExistenceTests(ApiTests):
    """Tests validating edx_uid lookups"""

    def test_invalid_params(self):
        """If no uid not set, 400"""
        resp = self.client.get(reverse('user-existence'))
        self.assertEqual(resp.status_code, 400)

    def test_no_user_exists(self):
        """If no uid not set, 400"""
        resp = self.client.get(reverse('user-existence'), {'uid': uuid.uuid4().hex})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.content.decode('utf-8')), {'exists': False})

    def test_user_exists(self):
        """If no uid not set, 400"""
        course = CourseFactory.create()
        author = EdxAuthorFactory.create(edx_uid=str(uuid.uuid4().hex))
        course.instructors.add(author)
        resp = self.client.get(reverse('user-existence'), {'uid': author.edx_uid})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.content.decode('utf-8')), {'exists': True})
