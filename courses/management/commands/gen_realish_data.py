"""
Generates fake data
"""
from django.core.management import BaseCommand

from courses.models import Course
from courses.factories import CourseFactory, ModuleFactory
from oauth_mgmt.factories import BackingInstanceFactory
from oauth_mgmt.models import BackingInstance


class Command(BaseCommand):
    """
    Generates fake data
    """
    help = "Generates data that looks real, but isn't"

    def handle(self, *args, **options):
        try:
            bi = BackingInstance.objects.get(instance_url='https://edx.org')
        except BackingInstance.DoesNotExist:
            bi = BackingInstanceFactory.create(instance_url='https://edx.org')

        course_title = 'Advanced Introductory Classical Mechanics'
        try:
            c = Course.objects.get(title=course_title)
            for m in c.module_set.all():
                m.delete()

        except Course.DoesNotExist:
            c = CourseFactory.create(
                edx_instance=bi,
                title=course_title,
                author_name='David E. Prichard',
                description='Mechanics ReView presents a college-level introductory mechanics '
                'class using a strategic problem-solving approach.',
                overview='For more information, see <a href="#">edx.org</a>',
                image_url='https://www.edx.org/sites/default/files/styles/course_video_banner'
                '/public/course/image/featured-card/8.mechcx-378x225.jpg',
            )

        module_names = """0: Introduction
        1: Newton's Laws of Motion
        2: Interactions and Forces
        3: Applying Newton's Laws
        4: Kinematics, the Mathematical Description of Motion
        5: Models of 1D Motion
        6: Applying SIM to Problems in Planar Dynamics
        7: System of Particles---Linear Momentum and Impulse
        8: Energy and Work
        9: Potential Energy and Mechanical Energy
        10: Torque and Rotation about a Fixed Axis
        11: Describing Rotational and Translational Motion
        12: Angular Momentum and Its Conservation
        13: Universal Gravity and Orbital Motion
        14: Simple Harmonic Oscillation
        15: Drag Forces
        Final Exam and Survey
        Optional Unit: Review for the AP Exam"""

        for i, module in enumerate(module_names.split('\n')):
            ModuleFactory.create(course=c, title=module.strip(), order=i)

        self.stdout.write("Done.")
