"""
Django Rest Framework Serializers for Course API
"""
import logging

from django.core.urlresolvers import reverse
from rest_framework import serializers

from .fields import JsonListField, StringyManyToManyField
from .models import Course, Module, EdxAuthor
from oauth_mgmt.models import BackingInstance

log = logging.getLogger(__name__)


class CourseSerializer(serializers.HyperlinkedModelSerializer):
    """
    Handles the serialization of Course objects.
    """
    edx_instance = serializers.SlugRelatedField(
        slug_field='instance_url',
        queryset=BackingInstance.objects.all(),
    )
    modules = serializers.SerializerMethodField('module_list')
    instructors = StringyManyToManyField(model=EdxAuthor, lookup="edx_uid")

    class Meta:  # pylint: disable=missing-docstring
        model = Course
        fields = (
            'uuid', 'title', 'author_name', 'overview', 'description',
            'image_url', 'edx_instance', 'url', 'modules', 'instructors',
            'course_id',
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
