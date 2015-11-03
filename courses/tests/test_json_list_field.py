# pylint: disable=missing-docstring
from django.test import TestCase

from rest_framework.serializers import ValidationError

from courses.serializers import JsonListField as JLF

class JsonListFieldTests(TestCase):
    def test_decodes_string(self):
        f = JLF()
        self.assertEquals([], f.to_internal_value('[]'))

    def test_decodes_unicode(self):
        f = JLF()
        self.assertEquals([], f.to_internal_value(u'[]'))

    def test_handles_decoding_nullable_values(self):
        f = JLF()
        self.assertEquals(None, f.to_internal_value('null'))

    def test_throws_validationerror_on_invalid_json(self):
        f = JLF()
        self.assertRaises(ValidationError, f.to_internal_value, 'testing')
