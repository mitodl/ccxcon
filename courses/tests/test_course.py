"""
Tests for Course
"""
from django.test import TestCase

from courses.models import Course


class CourseTests(TestCase):
    """
    Tests for Course
    """
    def test_tostring(self):
        """
        Test behavior of str(Course)
        """
        self.assertEqual(str(Course(title='test')), 'test')
