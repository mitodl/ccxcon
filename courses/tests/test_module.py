"""
Tests for Module
"""
from django.test import TestCase

from courses.models import Module


class ModuleTests(TestCase):
    """
    Tests for Module
    """
    def test_tostring(self):
        """
        Test behavior of str(Module)
        """
        self.assertEqual(str(Module(title='test')), 'test')
