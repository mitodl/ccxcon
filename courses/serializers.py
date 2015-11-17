"""
Django Rest Framework Serializers for Course API
"""
import json

from django.core.urlresolvers import reverse
from rest_framework import serializers
import six

from .models import Course, Module

import logging
log = logging.getLogger(__name__)


class JsonListField(serializers.Field):
    """
    Field which accepts and validates JSON arrays.
    """
    def to_representation(self, obj):
        "From a python object to a user-serializable state"
        return obj

    def to_internal_value(self, value):
        "Convert to a Python object"
        obj = []
        if isinstance(value, six.string_types):
            try:
                obj = json.loads(value)
            except ValueError as e:
                log.info(
                    "Could not parse JSON value: %s. Reason: %s", value, e)
                raise serializers.ValidationError("Must provide valid JSON.")

        if obj is not None and not isinstance(obj, list):
            raise serializers.ValidationError(
                "This field must be a JSON array")

        return obj


class CourseSerializer(serializers.HyperlinkedModelSerializer):
    """
    Handles the serialization of Course objects.
    """
    class Meta:  # pylint: disable=missing-docstring
        model = Course
        fields = (
            'uuid', 'title', 'author_name', 'overview', 'description',
            'video_url', 'edx_instance', 'price_per_seat_cents', 'url'
        )
        extra_kwargs = {
            'url': {'view_name': 'course-detail', 'lookup_field': 'uuid'}
        }


class ModuleSerializer(serializers.HyperlinkedModelSerializer):
    """
    Handles serialization of Module objects, including ensuring module
    is specific to the requested course.
    """
    course = serializers.HyperlinkedRelatedField(
        queryset=Course.objects.all(),
        view_name='course-detail',
        lookup_field='uuid'
    )
    subchapters = JsonListField()
    url = serializers.SerializerMethodField('absolute_url')

    class Meta:  # pylint: disable=missing-docstring
        model = Module
        fields = (
            'uuid', 'title', 'subchapters', 'course',
            'price_per_seat_cents', 'url'
        )

    def absolute_url(self, obj):
        """
        Builds absolute url for module instance.
        """
        request = self.context['request']
        return request.build_absolute_uri(
            reverse(
                'module-detail',
                kwargs={'uuid': obj.uuid, 'uuid_uuid': obj.course.uuid}
            )
        )
