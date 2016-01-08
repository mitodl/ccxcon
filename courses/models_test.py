"""
Tests for Models
"""
import json
from django.test import TestCase
from django.contrib.auth.models import User

from .factories import CourseFactory, ModuleFactory
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

    def test_towebhook(self):
        """
        test to_webhook implementation returns valid json object
        """
        course = CourseFactory.build()
        json.dumps(course.to_webhook())
        ex_pk = course.to_webhook()['external_pk']
        assert isinstance(ex_pk, str)
        assert '-' in ex_pk


class ModuleTests(TestCase):
    """
    Tests for Module
    """
    def test_tostring(self):
        """
        Test behavior of str(Module)
        """
        assert str(Module(title='test')) == 'test'

    def test_ordering(self):
        """
        Test module ordering is by course/order.
        """
        c1 = CourseFactory.create()
        c2 = CourseFactory.create()
        # Intentionally not in created in course-order so we can validate it's
        # not by id.
        m10 = ModuleFactory.create(course=c1, order=0)
        m21 = ModuleFactory.create(course=c2, order=1)
        m20 = ModuleFactory.create(course=c2, order=0)
        m11 = ModuleFactory.create(course=c1, order=1)

        result = [x.id for x in Module.objects.all()]

        assert result == [m10.id, m11.id, m20.id, m21.id]

    def test_towebhook(self):
        """
        test to_webhook implementation returns valid json object
        """
        module = ModuleFactory.build()
        web_out = module.to_webhook()
        json.dumps(web_out)
        for k in ('external_pk', 'course_external_pk'):
            assert isinstance(web_out[k], str)
            assert '-' in web_out[k]


class UserInfoTests(TestCase):
    """
    Tests for UserInfo
    """
    def test_tostring(self):
        """
        Test behavior of str(UserInfo)
        """
        assert str(UserInfo(user=User(username='test'))) == 'Profile for test'
