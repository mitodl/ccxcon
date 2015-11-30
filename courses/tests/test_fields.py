"""
Tests for Serializer Fields
"""
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
import pytest
from rest_framework.serializers import ValidationError

from courses.factories import EdxAuthorFactory, CourseFactory
from courses.models import EdxAuthor
from courses.serializers import JsonListField as JLF
from courses.serializers import StringyManyToManyField as SMMF


class JsonListFieldTests(TestCase):
    """
    Tests for JsonListField
    """
    def test_decodes_string(self):
        """
        Test that empty list string decodes properly
        """
        f = JLF()
        self.assertEqual([], f.to_internal_value('[]'))

    def test_decodes_unicode(self):
        """
        Test that empty list unicode string decodes properly
        """
        f = JLF()
        self.assertEqual([], f.to_internal_value(u'[]'))

    def test_handles_decoding_nullable_values(self):
        """
        Test that null is decoded to None
        """
        f = JLF()
        self.assertEqual(None, f.to_internal_value('null'))

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


class StringyM2MTestCase(TestCase):
    """Tests for m2m stringy field serializer"""
    def test_requires_model(self):
        """Field requires a model kwarg"""
        self.assertRaises(ImproperlyConfigured, SMMF, lookup='test')

    def test_requires_lookup(self):
        """Field requires a lookup kwarg"""
        self.assertRaises(ImproperlyConfigured, SMMF, model=EdxAuthor)

    def test_returns_string_for_all_objects(self):  # pylint: disable=no-self-use
        """model-to-string returns correct strings"""
        e1 = EdxAuthorFactory.create()
        e2 = EdxAuthorFactory.create()
        co = CourseFactory.create()
        co.instructors.add(e1)
        co.instructors.add(e2)

        f = SMMF(model=EdxAuthor, lookup='edx_uid')
        assert sorted([str(e1), str(e2)]) == sorted(f.to_representation(co.instructors))

    def test_returns_model_if_string_provided(self):  # pylint: disable=no-self-use
        """string-to-model returns correct model for single string"""
        uid = '2d133482b3214a119f55c3060d882ceb'
        CourseFactory.create()
        f = SMMF(model=EdxAuthor, lookup='edx_uid')
        ms = f.to_internal_value(uid)
        assert len(ms) == 1
        assert ms[0].edx_uid == uid

    def test_returns_models_if_list_provided(self):  # pylint: disable=no-self-use
        """string-to-model returns correct model for list"""
        uid = '2d133482b3214a119f55c3060d882ceb'
        uid2 = '3d133482b3214a119f55c3060d882ceb'
        CourseFactory.create()
        f = SMMF(model=EdxAuthor, lookup='edx_uid')
        ms = f.to_internal_value([uid, uid2])
        assert len(ms) == 2
        assert ms[0].edx_uid != ms[1].edx_uid
        assert ms[0].edx_uid in [uid, uid2]
        assert ms[1].edx_uid in [uid, uid2]

    def test_errors_on_invalid_input(self):  # pylint: disable=no-self-use
        """Only deserialize known, supported types."""
        CourseFactory.create()
        f = SMMF(model=EdxAuthor, lookup='edx_uid')
        with pytest.raises(ValidationError):
            f.to_internal_value(dict())
