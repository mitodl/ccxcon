"""
Generates fake data
"""
from random import randint
from django.core.management import BaseCommand

from courses.factories import CourseFactory, ModuleFactory
from oauth_mgmt.factories import BackingInstanceFactory
from oauth_mgmt.models import BackingInstance


class Command(BaseCommand):
    """
    Generates fake data
    """
    help = "Generates fake data"

    def add_arguments(self, parser):
        parser.add_argument(
            '--courses',
            dest='courses',
            default=3,
            help='Number of courses to generate',
        )

        parser.add_argument(
            '--modules',
            dest='modules',
            default=5,
            help='Number of modules to generate',
        )

    def handle(self, *args, **options):
        record_count = 0
        try:
            bi = BackingInstance.objects.get(instance_url='https://edx.org')
        except BackingInstance.DoesNotExist:
            bi = BackingInstanceFactory.create(instance_url='https://edx.org')
        for _ in range(int(options['courses'])):
            course = CourseFactory.create(edx_instance=bi)
            record_count += 1
            module_range = range(randint(1, int(options['modules'])))
            for _ in module_range:
                record_count += 1
                ModuleFactory.create(course=course)

        self.stdout.write("Wrote {} records.".format(record_count))
