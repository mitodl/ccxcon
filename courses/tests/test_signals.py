"""
Signal tests
"""
# pylint: disable=no-self-use
import mock

from django.test import TestCase

from courses.factories import CourseFactory, ModuleFactory


class PublishOnUpdateTests(TestCase):
    """
    Tests for webhook posting
    """
    def test_course_save_publishes(self):
        """
        When course is saved, it should trigger webhook.
        """
        course = CourseFactory.build()
        with mock.patch('courses.signals.publish_webhook', autospec=True) as wh_mock:
            course.save()
            assert wh_mock.delay.call_count == 1
            args, _ = wh_mock.delay.call_args
            assert args[0] == 'courses.Course'
            assert args[1] == 'uuid'
            assert args[2] == course.uuid

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
            assert args[2] == module.uuid
