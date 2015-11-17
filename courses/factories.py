"""Factories for testing"""
import factory
from factory.django import DjangoModelFactory
from .models import Module, Course


class CourseFactory(DjangoModelFactory):
    """Factory for Course"""
    class Meta:  # pylint: disable=missing-docstring
        model = Course


class ModuleFactory(DjangoModelFactory):
    """Factory for Module"""
    course = factory.SubFactory(CourseFactory)

    class Meta:  # pylint: disable=missing-docstring
        model = Module
