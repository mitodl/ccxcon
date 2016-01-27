"""Tests regarding REST API"""
import json
import re
import uuid

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
import mock
from requests.exceptions import RequestException

from courses.factories import CourseFactory, ModuleFactory, EdxAuthorFactory
from courses.models import EdxAuthor, Course
from oauth_mgmt.factories import BackingInstanceFactory

COURSE_ID = "course-locator:$org+$course.$run+branch+$branch+version+$version+type"


class ApiTests(TestCase):
    """Tests regarding REST API"""
    def setUp(self):
        self.user = User.objects.create_user('test', password='test')
        self.user.info.edx_instance = BackingInstanceFactory.create(instance_url='https://edx.org')
        self.user.info.save()
        assert self.client.login(username='test', password='test')


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
        self.assertEqual(len(payload), 1)

    def test_bad_json(self):
        """
        Test that invalid JSON is rejected and model state is unaffected.
        """
        course = CourseFactory.create(**{
            "title": "title1",
            "author_name": "author1",
            "overview": "overview1",
            "course_id": COURSE_ID,
            "description": "description1",
            "image_url": "http://placehold.it/350x150",
        })

        module_dict = {
            "title": "title",
            "subchapters": "['a', 3]",
        }
        modules_url = reverse('module-list', args=(course.uuid,))
        with mock.patch('courses.views.module_population', autospec=True):
            resp = self.client.post(modules_url, module_dict)
        self.assertEqual(resp.status_code, 400)  # Invalid JSON

        resp = self.client.get(modules_url)
        self.assertEqual(resp.status_code, 200, msg=resp.content)

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

            result = self.client.post(reverse('create-ccx'), payload)

            assert result.status_code == 400, result.content.decode('utf-8')
            assert re.search('POST argument.*{}'.format(key).encode(), result.content)

    def test_unknown_course_throws_404(self):
        """If we're given an unknown master_course_id, throw a 404"""
        result = self.client.post(reverse('create-ccx'), self.payload)

        assert result.status_code == 404, result.content.decode('utf-8')

    def test_request_error_returns_error(self):
        """If there's an error with the edx request, return an error"""
        course = CourseFactory.create()
        self.payload['master_course_id'] = str(course.uuid)

        with mock.patch('courses.views.requests', autospec=True) as mock_req:
            mock_req.post.side_effect = RequestException

            result = self.client.post(reverse('create-ccx'), self.payload)

            assert result.status_code == 502, result.content.decode('utf-8')

    def test_errory_status_code_returns_error(self):
        """If we get a status code from edx that looks error-y, throw an error"""
        course = CourseFactory.create()
        self.payload['master_course_id'] = str(course.uuid)

        with mock.patch('courses.views.requests', autospec=True) as mock_req:
            mock_req.post.return_value.status_code = 500
            mock_req.post.return_value.content = 'some error text'

            result = self.client.post(reverse('create-ccx'), self.payload)

            assert result.status_code == 502, result.content.decode('utf-8')

    def test_201_on_happy_case(self):
        """If all goes well, return 201"""
        course = CourseFactory.create()
        user_email = "john@example.com"
        seats = 123
        name = "CCX example title"

        with mock.patch('courses.views.requests', autospec=True) as mock_req:
            mock_req.post.return_value.status_code = 201

            result = self.client.post(reverse('create-ccx'), {
                'master_course_id': str(course.uuid),
                'user_email': user_email,
                'total_seats': seats,
                'display_name': name
            })

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
        result = self.client.post(reverse('create-ccx'), payload)
        assert result.status_code == 400, result.content.decode('utf-8')
        assert re.search(b'UUID do not belong to the specified master course', result.content)

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
            result = self.client.post(reverse('create-ccx'), payload)
        assert result.status_code == 201, result.content.decode('utf-8')
