"""
AppConfig
"""
from django.apps import AppConfig


class CourseConfig(AppConfig):
    """
    AppConfig to support signal registration
    """
    name = 'courses'

    def ready(self):
        from courses import signals  # pylint: disable=unused-variable
