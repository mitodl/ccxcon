"""
Signal tests
"""
# pylint: disable=no-self-use
import mock

from django.contrib.auth.models import User
from django.test import TestCase

from oauth_mgmt.factories import BackingInstanceFactory
from courses.models import UserInfo
from courses.factories import CourseFactory, ModuleFactory


class PublishOnUpdateTests(TestCase):
    """
    Tests for webhook posting
    """
    def test_course_save_publishes(self):
        """
        When course is saved, it should trigger webhook.
        """
        bi = BackingInstanceFactory.create()
        course = CourseFactory.build(edx_instance=bi)
        with mock.patch('courses.signals.publish_webhook', autospec=True) as wh_mock:
            course.save()
            assert wh_mock.delay.call_count == 1
            args, _ = wh_mock.delay.call_args
            assert args[0] == 'courses.Course'
            assert args[1] == 'uuid'
            assert args[2] == str(course.uuid)

    def test_module_save_publishes(self):
        """
        When module is saved, it should trigger webhook.
        """
        course = CourseFactory.create()
        module = ModuleFactory.build(course=course)
        with mock.patch('courses.signals.publish_webhook', autospec=True) as wh_mock:
            module.save()
            assert wh_mock.delay.call_count == 1
            args, _ = wh_mock.delay.call_args
            assert args[0] == 'courses.Module'
            assert args[1] == 'uuid'
            assert args[2] == str(module.uuid)


class CreateProfileTests(TestCase):
    """
    Tests for the user profile creation signal.
    """

    def test_creating_user_creates_profile(self):
        """
        We should get a profile after making a user.
        """
        assert not UserInfo.objects.exists()
        User.objects.create_user('test')
        assert UserInfo.objects.count() == 1

    def test_saving_existing_user_doesnt_create_profile(self):
        """
        We shouldn't get two profiles after updating.
        """
        user = User.objects.create_user('test')
        assert UserInfo.objects.count() == 1
        user.username = 'foo'
        user.save()
        assert UserInfo.objects.count() == 1
