"""
Tests for Models
"""
from django.test import TestCase
from django.contrib.auth.models import User

from courses.models import Course, Module, UserInfo
# pylint: disable=no-self-use


class CourseTests(TestCase):
    """
    Tests for Course
    """
    def test_tostring(self):
        """
        Test behavior of str(Course)
        """
        assert str(Course(title='test')) == 'test'


class ModuleTests(TestCase):
    """
    Tests for Module
    """
    def test_tostring(self):
        """
        Test behavior of str(Module)
        """
        assert str(Module(title='test')) == 'test'


class UserInfoTests(TestCase):
    """
    Tests for UserInfo
    """
    def test_tostring(self):
        """
        Test behavior of str(UserInfo)
        """
        assert str(UserInfo(user=User(username='test'))) == 'Profile for test'
