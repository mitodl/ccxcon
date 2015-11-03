# pylint: disable=missing-docstring
import factory
from factory.django import DjangoModelFactory
from .models import Module, Course

class CourseFactory(DjangoModelFactory):
    class Meta:
        model = Course

class ModuleFactory(DjangoModelFactory):
    course = factory.SubFactory(CourseFactory)
    class Meta:
        model = Module
