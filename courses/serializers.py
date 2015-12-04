"""
Django Rest Framework Serializers for Course API
"""
import json
import logging

from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.http import QueryDict
from rest_framework import serializers
import six

from .models import Course, Module, EdxAuthor

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


class StringyManyToManyField(serializers.Field):
    """
    Serializes out as a list of strings on the way out, but reifies into
    real models on the way in.
    """
    def __init__(self, *args, **kwargs):
        self.model = kwargs.pop('model', None)
        self.prop = kwargs.pop('lookup', None)

        if not self.model:
            raise ImproperlyConfigured("You must provide a model to use for reifying")

        if not self.prop:
            raise ImproperlyConfigured("You must provide a field lookup to "
                                       "convert string value into model instance.")

        super(StringyManyToManyField, self).__init__(*args, **kwargs)

    def to_representation(self, obj):
        """Python object to string"""
        return (str(i) for i in obj.all())

    def get_value(self, data):
        """Get all values provided, not just the first."""
        if isinstance(data, QueryDict):
            return data.getlist(self.field_name)
        return data.get(self.field_name)

    def to_internal_value(self, value):
        """Incoming value to python value.
        Values should only ever be a list or string."""
        if isinstance(value, six.string_types):
            value = [value]

        if not isinstance(value, list):
            raise serializers.ValidationError("Only supports string or list input types.")

        results = []
        for v in value:
            model, _ = self.model.objects.get_or_create(**{self.prop: v})
            results.append(model)
        return results


class CourseSerializer(serializers.HyperlinkedModelSerializer):
    """
    Handles the serialization of Course objects.
    """
    modules = serializers.SerializerMethodField('module_list')
    instructors = StringyManyToManyField(model=EdxAuthor, lookup="edx_uid")

    class Meta:  # pylint: disable=missing-docstring
        model = Course
        fields = (
            'uuid', 'title', 'author_name', 'overview', 'description',
            'image_url', 'edx_instance', 'url', 'modules', 'instructors',
        )
        extra_kwargs = {
            'url': {'view_name': 'course-detail', 'lookup_field': 'uuid'}
        }

    def module_list(self, obj):
        """
        Builds a url for module listing of this course.
        """
        return self.context['request'].build_absolute_uri(
            reverse('module-list', kwargs={'uuid_uuid': obj.uuid}))


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
            'uuid', 'title', 'subchapters', 'course', 'url'
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
