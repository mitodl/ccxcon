"""
Generates fake data
"""
from random import randint
from django.core.management import BaseCommand

from courses.factories import CourseFactory, ModuleFactory


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
        for _ in range(int(options['courses'])):
            course = CourseFactory.create()
            record_count += 1
            module_range = range(randint(1, int(options['modules'])))
            for _ in module_range:
                record_count += 1
                ModuleFactory.create(course=course)

        self.stdout.write("Wrote {} records.".format(record_count))
