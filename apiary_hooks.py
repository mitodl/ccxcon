import json
import os

import django
import dredd_hooks as hooks

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ccxcon.settings")
django.setup()

from courses.models import Course, Module

COURSE_UUID = '7e0e52d0386411df81ce001b631bdd31'
MODULE_UUID = '1db1a8439cbf4a8f8c395ad63fb43e8a'

dummyCourse = dict(
    uuid=COURSE_UUID,
    title="Introductory Physics: Classical Mechanics",
    author_name="David E. Pritchard",
    description="This is the description",
    video_url="",
    overview="This is the overview"
)

@hooks.after_each
def delete_data(transaction):
    Course.objects.all().delete()
    Module.objects.all().delete()

@hooks.before_all
def make_module_price_nullable(transactions):
    """
    Dredd doesn't yet expose nullable number fields, so we patch it in the before_all.
    """
    delete_data(None) # Clean up in case some error from last test is around.
    for t in transactions:
        try:
            schema = json.loads(t['expected']['bodySchema'])
            # This will throw a key error if this particular transaction
            # doesn't have an expected request with a `price_per_seat_cents`
            # field. We should silently ignore that.
            schema['properties']['price_per_seat_cents']['type'] = ['number', 'null']
            t['expected']['bodySchema'] = json.dumps(schema)
        except KeyError:
            pass


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

@hooks.before("Modules > Modules collection > List All modules  for a given Course")
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

@hooks.before("CCX Modules > Modules collection > List All modules associated with a given CCX")
def ccx_module_list(transaction):
    transaction['skip'] = True

@hooks.before("CCX Modules > Module membership > Add a module to a CCX Course")
def ccx_module_add(transaction):
    transaction['skip'] = True

@hooks.before("CCX Modules > Module membership > Delete a CCX")
def ccx_module_delete(transaction):
    transaction['skip'] = True
