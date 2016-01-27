"""test realish data gen script"""
# pylint: disable=no-self-use
from django.test import TestCase

from courses.models import Course, Module
from .gen_realish_data import Command


class RealishTestCase(TestCase):
    """test realish data gen script"""
    def test_makes_modules(self):
        """Should make course & modules"""
        Command().handle()

        assert Course.objects.count() == 1
        assert Module.objects.count() == 18

    def test_doesnt_double_create(self):
        """Shouldn't double make course & modules"""
        Command().handle()
        Command().handle()

        assert Course.objects.count() == 1
        assert Module.objects.count() == 18
