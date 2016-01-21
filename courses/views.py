"""
Views for powering the Course Catalog API
"""
import logging
from six.moves.urllib import parse

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
import requests
from requests.exceptions import RequestException
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework import serializers
from rest_framework.response import Response

from oauth_mgmt.utils import get_access_token
from .models import Course, Module, EdxAuthor
from .serializers import CourseSerializer, ModuleSerializer
from .tasks import module_population


log = logging.getLogger(__name__)


class CourseViewSet(viewsets.ModelViewSet):
    """
    Course API
    """
    queryset = Course.objects.all()
    lookup_field = 'uuid'
    serializer_class = CourseSerializer

    def create(self, request, *args, **kwargs):
        """
        Incoming call from edX.

        Because edX won't know if they've sent the information already or not,
        this handles the update and create case.

        It also does a bit of data preparation, setting the edx_instance from
        the authenticated user and prefixing image paths with this
        edx_instance.
        """
        user = request.user
        data = request.data.copy()
        if not user.info.edx_instance:
            raise serializers.ValidationError("User must have an associated edx_instance.")
        data['edx_instance'] = user.info.edx_instance

        if not data.get('image_url'):
            raise serializers.ValidationError("You must specify an image_url")
        data['image_url'] = parse.urljoin(
            user.info.edx_instance.instance_url, data['image_url'])

        # These two if blocks are majoritively copied directly from the source's
        # underlying mixins. It allows us to overwrite how we get the instance
        # to update without making a complex `get_object` override. Beyond that,
        # it allows us to not mutate the request.data object.
        if Course.objects.filter(course_id=data['course_id']).exists():
            # Mostly duped from rest_framework.mixins.UpdateModelMixin
            partial = kwargs.pop('partial', False)
            instance = Course.objects.get(course_id=data['course_id'])
            serializer = self.get_serializer(
                instance, data=data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            module_population.delay(serializer.instance.course_id)
            return Response(serializer.data)
        else:
            # Duped from rest_framework.mixins.CreateModelMixin for clarity.
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            module_population.delay(serializer.instance.course_id)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED, headers=headers)


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


@api_view(['POST'])
def create_ccx(request):
    """
    Supports creating a CCX on edx.

    Request parameters:
        master_course_id (string): UUID of the course you want to duplicate
        user_email (string): email address of the user to make CCX Coach
        display_name (string): Title of the CCX
        total_seats (int): Maximum number of students to allow into the ccx
        course_modules (list): Optional. List of strings representing course module UUIDs
    """
    def upstream_error(msg=None):
        """Generate logged errors for upstream response errors"""
        err = {
            'error': 'Unable to create course on upstream edx server. {}'.format(msg)
        }
        log.error(err['error'])
        return Response(err, status=502)
    missing = {
        x for x in ('master_course_id', 'user_email', 'total_seats', 'display_name')
        if x not in request.POST
    }
    if missing:
        raise serializers.ValidationError(detail={
            'error': 'You did not supply required POST argument(s): {}'.format(','.join(missing)),
        })

    course = get_object_or_404(Course, uuid=request.POST['master_course_id'])
    access_token = get_access_token(course.edx_instance)
    user_email = request.POST['user_email']

    payload = {
        'master_course_id': course.course_id,
        'coach_email': user_email,
        'max_students_allowed': request.POST['total_seats'],
        'display_name': request.POST['display_name'],
    }
    course_modules = request.POST.getlist('course_modules')
    if course_modules:
        course_modules_qs = Module.objects.filter(course=course, uuid__in=course_modules)
        if course_modules_qs.count() != len(course_modules):
            raise serializers.ValidationError(
                detail={
                    'error': (
                        'One or more course_modules UUID do '
                        'not belong to the specified master course'
                    )
                }
            )
        payload['course_modules'] = [
            course_module.locator_id for course_module in course_modules_qs
        ]

    try:
        resp = requests.post(
            '{instance}/api/ccx/v0/ccx/'.format(instance=course.edx_instance.instance_url),
            data=payload,
            headers={
                'Authorization': 'Bearer {}'.format(access_token),
            })
    except RequestException as e:
        return upstream_error(e)

    if resp.status_code >= 300:
        return upstream_error(resp.content)

    log.info(
        'Created ccx course for user %s on master course %s. Response: %s',
        user_email, course, resp.content)

    return Response(status=201)
