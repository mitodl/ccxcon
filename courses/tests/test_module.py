# pylint: disable=missing-docstring
from django.test import TestCase

from courses.models import Module

class ModuleTests(TestCase):
    def test_tostring(self):
        self.assertEqual(str(Module(title='test')), 'test')
