# pylint: disable=missing-docstring
from django.test import TestCase

from courses.models import Course

class CourseTests(TestCase):
    def test_tostring(self):
        self.assertEqual(str(Course(title='test')), 'test')
