# pylint: disable=missing-docstring
import json

from django.core.urlresolvers import reverse
from django.test import TestCase

from courses.factories import CourseFactory, ModuleFactory

class ApiTests(TestCase):
    def test_separate_children(self):
        m1 = ModuleFactory.create()
        m2 = ModuleFactory.create()

        # Different courses
        self.assertNotEqual(m1.course, m2.course)

        resp = self.client.get(reverse('module-list', args=(m1.course.uuid,)))
        payload = json.loads(resp.content.decode('utf-8'))
        self.assertEqual(len(payload), 1)

    def test_bad_json(self):
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
        resp = self.client.post(modules_url, module_dict)
        self.assertEqual(resp.status_code, 400)  # Invalid JSON

        resp = self.client.get(modules_url)
        self.assertEqual(resp.status_code, 200, resp.content)
