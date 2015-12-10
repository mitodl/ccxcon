"""Hooks for dredd tests."""
from datetime import datetime, timedelta

import django
import dredd_hooks as hooks  # pylint: disable=import-error

django.setup()

# pylint: disable=ungrouped-imports
# This import must come after django setup
from django.contrib.auth.models import User  # noqa
from oauth2_provider.models import Application, AccessToken  # noqa
from courses.models import Course, Module  # noqa


COURSE_UUID = '7e0e52d0386411df81ce001b631bdd31'
MODULE_UUID = '1db1a8439cbf4a8f8c395ad63fb43e8a'

dummyCourse = dict(
    uuid=COURSE_UUID,
    title="Introductory Physics: Classical Mechanics",
    author_name="David E. Pritchard",
    description="This is the description",
    image_url="http://placehold.it/350x150",
    overview="This is the overview"
)


@hooks.before_all
def create_user(transactions):
    """
    Creates necessary users and makes all requests authenticated.
    """
    app = Application.objects.create(
        name='oauth test app', user=User.objects.create_user('oauthapp'))
    user = User.objects.create_user('test', password='test')
    user.info.edx_instance = 'https://edx.org'
    user.info.save()
    token = AccessToken.objects.create(
        user=user, token='test-token', application=app,
        expires=datetime.now() + timedelta(days=1))

    for t in transactions:
        t['request']['headers']['Authorization'] = "Bearer {}".format(
            token.token)


# pylint: disable=missing-docstring
# pylint: disable=unused-argument
@hooks.after_each
def delete_data(transaction):
    Course.objects.all().delete()
    Module.objects.all().delete()


@hooks.before("Courses > Courses Collection > List All Courses")
def course_list(transaction):
    Course(**dummyCourse).save()


@hooks.before("Courses > Course > Retrieve a Course")
def course_get(transaction):
    Course(**dummyCourse).save()


@hooks.before("Courses > Course > Delete Course")
def course_delete(transaction):
    Course(**dummyCourse).save()


@hooks.before("Courses > Course > Partially update Course")
def course_partial_update(transaction):
    transaction['skip'] = True


@hooks.before("Courses > Course > Update Course")
def course_update(transaction):
    Course.objects.create(uuid=COURSE_UUID)


@hooks.before(
    "Modules > Modules collection > List All modules  for a given Course")
def module_list(transaction):
    Course.objects.create(uuid=COURSE_UUID)


@hooks.before("Modules > Modules collection > Create a New Module")
def module_create(transaction):
    Course.objects.create(uuid=COURSE_UUID)


@hooks.before("Modules > Module > Retrieve a Module")
def module_get(transaction):
    course = Course.objects.create(uuid=COURSE_UUID)
    Module.objects.create(uuid=MODULE_UUID, course=course)


@hooks.before("Modules > Module > Delete a Module")
def module_delete(transaction):
    course = Course.objects.create(uuid=COURSE_UUID)
    Module.objects.create(uuid=MODULE_UUID, course=course)


@hooks.before("Modules > Module > Partially update a Module")
def module_partial_update(transaction):
    transaction['skip'] = True


@hooks.before("Modules > Module > Update a Module")
def module_update(transaction):
    course = Course.objects.create(uuid=COURSE_UUID)
    Module.objects.create(uuid=MODULE_UUID, course=course)


@hooks.before("CCXs > CCX Collection > List All CCXs  for a given Course")
def ccx_list(transaction):
    transaction['skip'] = True


@hooks.before("CCXs > CCX Collection > Create a New CCX Course")
def ccx_new(transaction):
    transaction['skip'] = True


@hooks.before("CCXs > CCX > Retrieve a CCX")
def ccx_get(transaction):
    transaction['skip'] = True


@hooks.before("CCXs > CCX > Delete a CCX")
def ccx_delete(transaction):
    transaction['skip'] = True


@hooks.before("CCXs > CCX > Partially update a CCX")
def ccx_partial_update(transaction):
    transaction['skip'] = True


@hooks.before("CCXs > CCX > Update a CCX")
def ccx_update(transaction):
    transaction['skip'] = True


@hooks.before(
    "CCX Modules > Modules collection > "
    "List All modules associated with a given CCX")
def ccx_module_list(transaction):
    transaction['skip'] = True


@hooks.before("CCX Modules > Module membership > Add a module to a CCX Course")
def ccx_module_add(transaction):
    transaction['skip'] = True


@hooks.before("CCX Modules > Module membership > Delete a CCX")
def ccx_module_delete(transaction):
    transaction['skip'] = True
