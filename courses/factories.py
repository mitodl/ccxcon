"""Factories for testing"""
from uuid import uuid4
import factory
from factory.django import DjangoModelFactory
from .models import Module, Course, EdxAuthor


class EdxAuthorFactory(DjangoModelFactory):
    """Factory for EdxAuthor"""
    edx_uid = factory.LazyAttribute(lambda x: uuid4().hex)

    class Meta:  # pylint: disable=missing-docstring
        model = EdxAuthor


class CourseFactory(DjangoModelFactory):
    """Factory for Course"""

    class Meta:  # pylint: disable=missing-docstring
        model = Course


class ModuleFactory(DjangoModelFactory):
    """Factory for Module"""
    course = factory.SubFactory(CourseFactory)

    class Meta:  # pylint: disable=missing-docstring
        model = Module
