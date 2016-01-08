"""Hooks for dredd tests."""
from datetime import datetime, timedelta

import django
import dredd_hooks as hooks  # pylint: disable=import-error

django.setup()

# pylint: disable=ungrouped-imports
# This import must come after django setup
from django.contrib.auth.models import User  # noqa
from oauth2_provider.models import Application, AccessToken  # noqa
from oauth_mgmt.factories import BackingInstanceFactory  # noqa
from oauth_mgmt.models import BackingInstance  # noqa
from courses.factories import CourseFactory  # noqa
from courses.models import Course, Module  # noqa


COURSE_UUID = '7e0e52d0386411df81ce001b631bdd31'
MODULE_UUID = '1db1a8439cbf4a8f8c395ad63fb43e8a'

dummyCourse = dict(
    uuid=COURSE_UUID,
    title="Introductory Physics: Classical Mechanics",
    author_name="David E. Pritchard",
    description="This is the description",
    image_url="http://placehold.it/350x150",
    overview="This is the overview",
)


@hooks.before_all
def create_user(transactions):
    """
    Creates necessary users and makes all requests authenticated.
    """
    app_user = User.objects.create_user('oauthapp')
    app = Application.objects.create(
        name='oauth test app', user=app_user)
    app_user.info.edx_instance = BackingInstanceFactory.create(instance_url='https://edx.org')
    app_user.info.save()

    # Explicitly not setting user on the AccessToken, as we don't do this in the
    # actual token generation code.
    token = AccessToken.objects.create(
        token='test-token', application=app,
        expires=datetime.now() + timedelta(days=1))

    for t in transactions:
        t['request']['headers']['Authorization'] = "Bearer {}".format(
            token.token)


def gen_course(**kwargs):
    """
    Generate a course using dummyCourse info, proxying back to the CourseFactory.
    """
    attrs = dummyCourse.copy()
    attrs.update(edx_instance=BackingInstance.objects.get(instance_url='https://edx.org'))
    attrs.update(kwargs)
    return CourseFactory.create(**attrs)


# pylint: disable=missing-docstring,unused-argument
@hooks.after_each
def delete_data(transaction):
    Course.objects.all().delete()
    Module.objects.all().delete()


@hooks.before("Courses > Courses Collection > List All Courses")
def course_list(transaction):
    gen_course()


@hooks.before("Courses > Course > Retrieve a Course")
def course_get(transaction):
    gen_course()


@hooks.before("Courses > Course > Delete Course")
def course_delete(transaction):
    gen_course()


@hooks.before("Courses > Course > Partially update Course")
def course_partial_update(transaction):
    transaction['skip'] = True


@hooks.before("Courses > Course > Update Course")
def course_update(transaction):
    gen_course(uuid=COURSE_UUID)


@hooks.before(
    "Modules > Modules collection > List All modules  for a given Course")
def module_list(transaction):
    gen_course(uuid=COURSE_UUID)


@hooks.before("Modules > Modules collection > Create a New Module")
def module_create(transaction):
    gen_course(uuid=COURSE_UUID)


@hooks.before("Modules > Module > Retrieve a Module")
def module_get(transaction):
    course = gen_course(uuid=COURSE_UUID)
    Module.objects.create(uuid=MODULE_UUID, course=course)


@hooks.before("Modules > Module > Delete a Module")
def module_delete(transaction):
    course = gen_course(uuid=COURSE_UUID)
    Module.objects.create(uuid=MODULE_UUID, course=course)


@hooks.before("Modules > Module > Partially update a Module")
def module_partial_update(transaction):
    transaction['skip'] = True


@hooks.before("Modules > Module > Update a Module")
def module_update(transaction):
    course = gen_course(uuid=COURSE_UUID)
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
