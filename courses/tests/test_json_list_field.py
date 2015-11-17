"""
Tests for JsonListField
"""
from django.test import TestCase

from rest_framework.serializers import ValidationError

from courses.serializers import JsonListField as JLF


class JsonListFieldTests(TestCase):
    """
    Tests for JsonListField
    """
    def test_decodes_string(self):
        """
        Test that empty list string decodes properly
        """
        f = JLF()
        self.assertEquals([], f.to_internal_value('[]'))

    def test_decodes_unicode(self):
        """
        Test that empty list unicode string decodes properly
        """
        f = JLF()
        self.assertEquals([], f.to_internal_value(u'[]'))

    def test_handles_decoding_nullable_values(self):
        """
        Test that null is decoded to None
        """
        f = JLF()
        self.assertEquals(None, f.to_internal_value('null'))

    def test_throws_validationerror_on_invalid_json(self):
        """
        Test invalid JSON
        """
        f = JLF()
        self.assertRaises(ValidationError, f.to_internal_value, 'testing')

    def test_not_list(self):
        """
        Test that to_internal_value takes only lists
        """
        f = JLF()
        self.assertRaises(ValidationError, f.to_internal_value, '{}')
