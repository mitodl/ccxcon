"""
Views for powering the Course Catalog API
"""
from django.core.urlresolvers import reverse

from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Course, Module, EdxAuthor
from .serializers import CourseSerializer, ModuleSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """
    Course API
    """
    queryset = Course.objects.all()
    lookup_field = 'uuid'
    serializer_class = CourseSerializer


class ModuleViewSet(viewsets.ModelViewSet):
    """
    Module API
    """
    queryset = Module.objects.all()
    lookup_field = 'uuid'
    serializer_class = ModuleSerializer

    def create(self, request, **kwargs):
        # uuid_uuid is the uuid field of the parent resource (Course)
        request.data['course'] = reverse(
            'course-detail', args=(kwargs['uuid_uuid'],))
        return super(ModuleViewSet, self).create(request, **kwargs)

    def update(self, request, **kwargs):
        # uuid_uuid is the uuid field of the parent resource (Course)
        request.data['course'] = reverse(
            'course-detail', args=(kwargs['uuid_uuid'],))
        return super(ModuleViewSet, self).update(request, **kwargs)

    def list(self, request, uuid_uuid):
        "List of modules filtered by parent course."
        modules = self.queryset.filter(course__uuid=uuid_uuid)
        serializer = self.serializer_class(
            modules, many=True, context={'request': request})
        return Response(serializer.data)


@api_view()
def user_existence(request):
    """
    Support for validating the existence of users, ensuring that they
    represent a real edx author.
    """
    uid = request.GET.get('uid')
    if not uid:
        return Response({"error": "Must provide a UID"}, status=400)

    return Response({"exists": EdxAuthor.objects.filter(edx_uid=uid).exists()})
