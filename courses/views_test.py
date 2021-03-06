"""Tests regarding REST API"""
import json
import re
import uuid

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase, RequestFactory
import mock
from requests.exceptions import RequestException

from courses.factories import CourseFactory, ModuleFactory, EdxAuthorFactory
from courses.models import EdxAuthor, Course
from oauth_mgmt.factories import BackingInstanceFactory
from oauth_mgmt.utils import UnretrievableToken

COURSE_ID = "course-locator:$org+$course.$run+branch+$branch+version+$version+type"


class ApiTests(TestCase):
    """Tests regarding REST API"""
    def setUp(self):
        self.user = User.objects.create_user('test', password='test')
        self.user.info.edx_instance = BackingInstanceFactory.create(instance_url='https://edx.org')
        self.user.info.save()
        assert self.client.login(username='test', password='test')


def course_detail_dict(course):
    """Helper function to produce the expected course detail response"""
    # Request so we can call build_absolute_uri
    request = RequestFactory().get("")
    return {
        "uuid": str(course.uuid),
        "title": course.title,
        "author_name": course.author_name,
        "overview": course.overview,
        "description": course.description,
        "image_url": course.image_url,
        "edx_instance": course.edx_instance.instance_url,
        "url": request.build_absolute_uri(reverse('course-detail', kwargs={
            'uuid': str(course.uuid)
        })),
        "modules": request.build_absolute_uri(reverse('module-list', kwargs={
            'uuid_uuid': str(course.uuid)
        })),
        "instructors": [],
        "course_id": course.course_id
    }


def module_detail_dict(module):
    """Helper function to produce the expected module detail response"""
    # Request so we can call build_absolute_uri
    request = RequestFactory().get("")
    return {
        "uuid": str(module.uuid),
        "title": str(module.title),
        "subchapters": module.subchapters,
        "course": request.build_absolute_uri(reverse('course-detail', kwargs={
            "uuid": str(module.course.uuid)
        })),
        "url": request.build_absolute_uri(reverse('module-detail', kwargs={
            "uuid": str(module.uuid),
            "uuid_uuid": str(module.course.uuid),
        }))
    }


class JsonResponseTests(ApiTests):
    """
    Tests that json responses are what we expect.
    """
    def test_separate_children(self):
        """
        Test that a course's modules list endpoint doesn't contain modules
        from other courses.
        """
        m1 = ModuleFactory.create()
        m2 = ModuleFactory.create()

        # Different courses
        self.assertNotEqual(m1.course, m2.course)

        resp = self.client.get(reverse('module-list', args=(m1.course.uuid,)))
        payload = json.loads(resp.content.decode('utf-8'))
        assert payload == [module_detail_dict(m1)]

    def test_create_course_accepts_instructors(self):
        """
        Validate course create endpoint accepts instructors
        """
        with mock.patch('courses.views.module_population', autospec=True):
            resp = self.client.post(reverse('course-list'), {
                "title": "title1",
                "author_name": "author1",
                "overview": "overview1",
                "description": "description1",
                "image_url": "http://placehold.it/350x150",
                "course_id": COURSE_ID,
                "edx_instance": "http://edx.org/",
                "instructors": [
                    "861e87a0803e436b989cb62d5e672c5f",
                    "961e87a0803e436b989cb62d5e672c5f"
                ]
            })
        self.assertEqual(resp.status_code, 201, msg=resp.content)
        assert EdxAuthor.objects.count() == 2

    def test_get_course_list(self):
        """
        The course list API should list all courses available.
        """
        course = CourseFactory.create()
        resp = self.client.get(reverse('course-list'))
        assert resp.status_code == 200, resp.content.decode('utf-8')
        course_list = json.loads(resp.content.decode('utf-8'))
        assert course_list == [course_detail_dict(course)]

        # Make sure users not logged in can't list courses
        self.client.logout()
        resp = self.client.get(reverse('course-list'))
        assert resp.status_code == 401, resp.content.decode('utf-8')

    def test_get_course_detail(self):
        """
        The course detail API should show information about a specific course.
        """
        course = CourseFactory.create()
        resp = self.client.get(reverse('course-detail', kwargs={"uuid": str(course.uuid)}))
        assert resp.status_code == 200, resp.content.decode('utf-8')
        course_detail = json.loads(resp.content.decode('utf-8'))
        assert course_detail == course_detail_dict(course)

        # Make sure users not logged in can't see the course detail view
        self.client.logout()
        resp = self.client.get(reverse('course-detail', kwargs={"uuid": str(course.uuid)}))
        assert resp.status_code == 401, resp.content.decode('utf-8')

    def test_get_module_detail(self):
        """
        The module detail API should show information about a specific module.
        """
        module = ModuleFactory.create()

        resp = self.client.get(reverse('module-detail', kwargs={
            "uuid_uuid": module.course.uuid,
            "uuid": module.uuid
        }))
        assert resp.status_code == 200, resp.content.decode('utf-8')
        payload = json.loads(resp.content.decode('utf-8'))
        assert payload == module_detail_dict(module)

        # Make sure users not logged in can't list courses
        self.client.logout()
        resp = self.client.get(reverse('module-detail', kwargs={
            "uuid_uuid": module.course.uuid,
            "uuid": module.uuid
        }))
        assert resp.status_code == 401, resp.content.decode('utf-8')

    def test_illegal_methods(self):
        """
        Assert that we are not using certain HTTP methods.
        """
        module = ModuleFactory.create()
        course_list = reverse('course-list')
        course_detail = reverse('course-detail', kwargs={"uuid": module.course.uuid})
        module_list = reverse('module-list', kwargs={"uuid_uuid": module.course.uuid})
        module_detail = reverse('module-detail', kwargs={
            "uuid_uuid": module.course.uuid,
            "uuid": module.uuid
        })

        for url in (course_list, course_detail, module_list, module_detail):
            assert self.client.patch(url).status_code == 405
            assert self.client.put(url).status_code == 405
            assert self.client.delete(url).status_code == 405

        for url in (course_detail, module_list, module_detail):
            assert self.client.post(url).status_code == 405

    def test_create_course_does_module_population(self):
        """
        Ensure we actually call out to module population code.
        """
        with mock.patch('courses.views.module_population', autospec=True) as mock_pop:
            self.client.post(reverse('course-list'), {
                "title": "title1",
                "author_name": "author1",
                "overview": "overview1",
                "description": "description1",
                "image_url": "http://placehold.it/350x150",
                "course_id": COURSE_ID,
                "edx_instance": "http://edx.org/",
                "instructors": [
                    "861e87a0803e436b989cb62d5e672c5f",
                    "961e87a0803e436b989cb62d5e672c5f"
                ]
            })
            assert mock_pop.delay.called

    def test_edx_instance_applied_automatically(self):
        """
        edx_instance applied automatically.
        """
        with mock.patch('courses.views.module_population', autospec=True):
            resp = self.client.post(reverse('course-list'), {
                "title": "title1",
                "author_name": "author1",
                "overview": "overview1",
                "description": "description1",
                "image_url": "http://youtube.com/1",
                "course_id": COURSE_ID,
                "edx_instance": "",
                "instructors": [
                    "861e87a0803e436b989cb62d5e672c5f",
                    "961e87a0803e436b989cb62d5e672c5f"
                ]
            })
        self.assertEqual(resp.status_code, 201, msg=resp.content)
        assert Course.objects.all()[0].edx_instance.instance_url == 'https://edx.org'

    def test_requires_edx_instance(self):
        """
        If no edx_instance available, throw error
        """
        User.objects.create_user('no-instance', password='test')
        assert self.client.login(username='no-instance', password='test')
        with mock.patch('courses.views.module_population', autospec=True):
            resp = self.client.post(reverse('course-list'), {
                "title": "title1",
                "author_name": "author1",
                "overview": "overview1",
                "description": "description1",
                "image_url": "http://youtube.com/1",
                "course_id": COURSE_ID,
                "edx_instance": "",
                "instructors": [
                    "861e87a0803e436b989cb62d5e672c5f",
                    "961e87a0803e436b989cb62d5e672c5f"
                ]
            })
        self.assertEqual(resp.status_code, 400, resp.content)

    def test_image_url_as_path_is_okay(self):
        """
        image_urls can be just paths.
        """
        with mock.patch('courses.views.module_population', autospec=True):
            resp = self.client.post(reverse('course-list'), {
                "title": "title1",
                "author_name": "author1",
                "overview": "overview1",
                "description": "description1",
                "course_id": COURSE_ID,
                "image_url": "/1",
                "instructors": [
                    "861e87a0803e436b989cb62d5e672c5f",
                    "961e87a0803e436b989cb62d5e672c5f"
                ]
            })
        self.assertEqual(resp.status_code, 201, resp.content)
        assert Course.objects.all()[0].image_url == "{}/1".format(
            self.user.info.edx_instance)

    def test_image_url_required(self):
        """
        image_urls are still required
        """
        with mock.patch('courses.views.module_population', autospec=True):
            resp = self.client.post(reverse('course-list'), {
                "title": "title1",
                "author_name": "author1",
                "overview": "overview1",
                "description": "description1",
                "course_id": COURSE_ID,
                "instructors": [
                    "861e87a0803e436b989cb62d5e672c5f",
                    "961e87a0803e436b989cb62d5e672c5f"
                ]
            })
        self.assertEqual(resp.status_code, 400, resp.content)
        assert 'must specify an image_url' in resp.content.decode('utf-8')

    def test_image_url_required_when_blank(self):
        """
        image_urls are still required even if blank
        """
        with mock.patch('courses.views.module_population', autospec=True):
            resp = self.client.post(reverse('course-list'), {
                "title": "title1",
                "author_name": "author1",
                "overview": "overview1",
                "description": "description1",
                "image_url": "",
                "course_id": COURSE_ID,
                "instructors": [
                    "861e87a0803e436b989cb62d5e672c5f",
                    "961e87a0803e436b989cb62d5e672c5f"
                ]
            })
        self.assertEqual(resp.status_code, 400, resp.content)
        assert 'must specify an image_url' in resp.content.decode('utf-8')

    def test_duplicate_post_doesnt_create(self):
        """
        If we post twice with the same course_id, it should trigger an update.
        """
        with mock.patch('courses.views.module_population', autospec=True):
            resp = self.client.post(reverse('course-list'), {
                "title": "title1",
                "author_name": "author1",
                "overview": "overview1",
                "description": "description1",
                "course_id": COURSE_ID,
                "image_url": "/234.jpg",
                "instructors": [
                    "861e87a0803e436b989cb62d5e672c5f",
                    "961e87a0803e436b989cb62d5e672c5f"
                ]
            })
            self.assertEqual(resp.status_code, 201, resp.content)
            resp = self.client.post(reverse('course-list'), {
                "title": "title1",
                "author_name": "author1",
                "overview": "overview1",
                "description": "description1",
                "course_id": COURSE_ID,
                "image_url": "/234.jpg",
                "instructors": [
                    "861e87a0803e436b989cb62d5e672c5f",
                    "961e87a0803e436b989cb62d5e672c5f"
                ]
            })
            self.assertEqual(resp.status_code, 200, resp.content)
            assert Course.objects.count() == 1


class UserExistenceTests(ApiTests):
    """Tests validating edx_uid lookups"""

    def test_invalid_params(self):
        """If no uid not set, 400"""
        resp = self.client.get(reverse('user-existence'))
        self.assertEqual(resp.status_code, 400)

    def test_no_user_exists(self):
        """If no uid not set, 400"""
        resp = self.client.get(reverse('user-existence'), {'uid': uuid.uuid4().hex})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.content.decode('utf-8')), {'exists': False})

    def test_user_exists(self):
        """If no uid not set, 400"""
        course = CourseFactory.create()
        author = EdxAuthorFactory.create(edx_uid=str(uuid.uuid4().hex))
        course.instructors.add(author)
        resp = self.client.get(reverse('user-existence'), {'uid': author.edx_uid})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.content.decode('utf-8')), {'exists': True})


# pylint: disable=no-self-use
class CCXCreateTests(ApiTests):
    """Test CCX create API for making CCXs on edx"""

    def setUp(self):
        self.payload = {
            'master_course_id': '7955ceaa-c076-4a21-82f0-09527a8c8b7e',
            'user_email': 'bleh@example.com',
            'total_seats': 102,
            'display_name': 'test name',
        }
        super(CCXCreateTests, self).setUp()

    def test_missing_arguments_throw_error(self):
        """Throw an error if we're missing a POST parameter"""
        for key in ['master_course_id', 'user_email', 'total_seats', 'display_name']:
            payload = self.payload.copy()
            del payload[key]

            result = self.client.post(
                reverse('create-ccx'),
                json.dumps(payload),
                content_type="application/json"
            )

            assert result.status_code == 400, result.content.decode('utf-8')
            assert 'error' in result.json().keys()
            assert re.search('POST argument.*{}'.format(key), result.json()['error'])

    def test_unknown_course_throws_404(self):
        """If we're given an unknown master_course_id, throw a 404"""
        result = self.client.post(
            reverse('create-ccx'),
            json.dumps(self.payload),
            content_type="application/json"
        )

        assert result.status_code == 404, result.content.decode('utf-8')

    def test_request_error_returns_error(self):
        """If there's an error with the edx request, return an error"""
        course = CourseFactory.create()
        self.payload['master_course_id'] = str(course.uuid)

        with mock.patch('courses.views.requests', autospec=True) as mock_req:
            mock_req.post.side_effect = RequestException

            result = self.client.post(
                reverse('create-ccx'),
                json.dumps(self.payload),
                content_type="application/json"
            )

            assert result.status_code == 502, result.content.decode('utf-8')
            assert 'Could not make request' in result.json()['error']

    def test_errory_status_code_returns_error(self):
        """If we get a status code from edx that looks error-y, throw an error"""
        course = CourseFactory.create()
        self.payload['master_course_id'] = str(course.uuid)

        with mock.patch('courses.views.requests', autospec=True) as mock_req:
            mock_req.post.return_value.status_code = 500
            mock_req.post.return_value.json.return_value = {}

            result = self.client.post(
                reverse('create-ccx'),
                json.dumps(self.payload),
                content_type="application/json"
            )

            assert result.status_code == 502, result.content.decode('utf-8')
            assert 'Invalid status code' in result.json()['error']

    def test_201_on_happy_case(self):
        """If all goes well, return 201"""
        course = CourseFactory.create()
        user_email = "john@example.com"
        seats = 123
        name = "CCX example title"

        with mock.patch('courses.views.requests', autospec=True) as mock_req:
            mock_req.post.return_value.status_code = 201
            mock_req.post.return_value.json.return_value = {}

            result = self.client.post(reverse('create-ccx'), json.dumps({
                'master_course_id': str(course.uuid),
                'user_email': user_email,
                'total_seats': seats,
                'display_name': name
            }), content_type="application/json")

            assert result.status_code == 201, result.content.decode('utf-8')

    def test_course_modules_must_belong_to_course(self):
        """
        Test with course modules not belonging to the course
        """
        payload = self.payload.copy()
        course = CourseFactory.create()
        payload['master_course_id'] = str(course.uuid)
        course_modules_real = [str(ModuleFactory(course=course).uuid) for _ in range(5)]
        course_modules_fake = [uuid.uuid4().hex for _ in range(5)]
        payload['course_modules'] = course_modules_real + course_modules_fake
        result = self.client.post(
            reverse('create-ccx'),
            json.dumps(payload),
            content_type="application/json"
        )
        assert result.status_code == 400, result.content.decode('utf-8')
        assert re.search('UUID do not belong to the specified master course',
                         result.json()['error'])

    def test_201_on_happy_case_with_modules(self):
        """
        Same as test_201_on_happy_case, but with a list of course modules
        """
        payload = self.payload.copy()
        course = CourseFactory.create()
        payload['master_course_id'] = str(course.uuid)
        course_modules = [ModuleFactory(course=course) for _ in range(10)]
        payload['course_modules'] = [str(course_module.uuid) for course_module in course_modules]

        with mock.patch('courses.views.requests', autospec=True) as mock_req:
            mock_req.post.return_value.status_code = 201
            mock_req.post.return_value.json.return_value = {}

            result = self.client.post(
                reverse('create-ccx'),
                json.dumps(payload),
                content_type="application/json"
            )
        assert result.status_code == 201, result.content.decode('utf-8')
        # check that the payload has been sent to edx as json
        # this means that the requests library will encode it properly
        # and add the `application/json` content type header
        call_to_edx = mock_req.post.call_args
        call_content = call_to_edx[1]
        assert 'json' in call_content
        payload_to_edx = {
            'course_modules': [course_module.locator_id for course_module in course_modules],
            'coach_email': payload['user_email'],
            'master_course_id': course.course_id,
            'display_name': payload['display_name'],
            'max_students_allowed': payload['total_seats']
        }
        for key, value in payload_to_edx.items():
            assert key in call_content['json']
            if not isinstance(value, list):
                assert value == call_content['json'][key]
            else:
                assert sorted(value) == sorted(call_content['json'][key])

    def test_not_logged_in(self):
        """
        Test that users who are not logged in can't do anything.
        """
        self.client.logout()

        course = CourseFactory.create()
        user_email = "john@example.com"
        seats = 123
        name = "CCX example title"

        result = self.client.post(reverse('create-ccx'), json.dumps({
            'master_course_id': str(course.uuid),
            'user_email': user_email,
            'total_seats': seats,
            'display_name': name
        }), content_type="application/json")

        assert result.status_code == 401, result.content.decode('utf-8')

    def test_access_token_fails(self):
        """
        If we can't get an access token, give a reasonable error.
        """
        course = CourseFactory.create()
        user_email = "john@example.com"
        seats = 123
        name = "CCX example title"

        with mock.patch('courses.views.get_access_token', autospec=True) as token:
            token.side_effect = UnretrievableToken

            result = self.client.post(reverse('create-ccx'), json.dumps({
                'master_course_id': str(course.uuid),
                'user_email': user_email,
                'total_seats': seats,
                'display_name': name
            }), content_type="application/json")

        assert "Could not fetch access token" in result.json()['error']
