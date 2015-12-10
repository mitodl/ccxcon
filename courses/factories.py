"""Factories for testing"""
from uuid import uuid4
import random
import factory
from factory import fuzzy
from factory.django import DjangoModelFactory
import faker

from .models import Module, Course, EdxAuthor

fake = faker.Factory.create()


class EdxAuthorFactory(DjangoModelFactory):
    """Factory for EdxAuthor"""
    edx_uid = factory.LazyAttribute(lambda x: uuid4().hex)

    class Meta:  # pylint: disable=missing-docstring
        model = EdxAuthor


class CourseFactory(DjangoModelFactory):
    """Factory for Course"""
    title = fuzzy.FuzzyText(prefix="Course ")
    author_name = factory.LazyAttribute(lambda x: fake.name())
    edx_instance = "https://edx.org/"
    overview = factory.LazyAttribute(lambda x: fake.text())
    description = factory.LazyAttribute(lambda x: fake.text())
    course_id = fuzzy.FuzzyText(length=30)

    class Meta:  # pylint: disable=missing-docstring
        model = Course


class ModuleFactory(DjangoModelFactory):
    """Factory for Module"""
    course = factory.SubFactory(CourseFactory)
    title = fuzzy.FuzzyText(prefix="Module ")

    class Meta:  # pylint: disable=missing-docstring
        model = Module

    @factory.lazy_attribute
    def subchapters(self):  # pylint: disable=no-self-use
        """
        Generate subchapter listing.
        """
        rand = random.Random(fuzzy.get_random_state())
        total = rand.randint(3, 12)
        return [fake.sentence(
            nb_words=6, variable_nb_words=True) for _ in range(total)]
