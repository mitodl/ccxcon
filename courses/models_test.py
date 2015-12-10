"""
Tests for Models
"""
from django.test import TestCase

from courses.models import Course, Module


class CourseTests(TestCase):
    """
    Tests for Course
    """
    def test_tostring(self):
        """
        Test behavior of str(Course)
        """
        self.assertEqual(str(Course(title='test')), 'test')


class ModuleTests(TestCase):
    """
    Tests for Module
    """
    def test_tostring(self):
        """
        Test behavior of str(Module)
        """
        self.assertEqual(str(Module(title='test')), 'test')
