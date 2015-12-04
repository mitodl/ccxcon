"""
Models necessary to represent a course catalog.
"""
import uuid as pyuuid

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from jsonfield import JSONField


@python_2_unicode_compatible
class EdxAuthor(models.Model):
    """
    Represents an author on edX.
    """
    edx_uid = models.UUIDField(
        default=pyuuid.uuid4, unique=True,
        help_text="Unique ID generated by the edx-platform")

    def __repr__(self):
        return "<EdxAuthor edx_uid={}>".format(self.edx_uid.hex)

    def __str__(self):
        return self.edx_uid.hex


@python_2_unicode_compatible
class Course(models.Model):
    """
    An edX course which is purchasable.
    """
    uuid = models.UUIDField(default=pyuuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    author_name = models.CharField(max_length=255)
    overview = models.TextField()
    description = models.TextField()
    image_url = models.URLField()
    instructors = models.ManyToManyField(EdxAuthor)

    edx_instance = models.URLField(max_length=255)
    live = models.BooleanField(default=False)

    deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return self.title


@python_2_unicode_compatible
class Module(models.Model):
    """
    Represents a purchasable 'chapter' of a course.
    """
    uuid = models.UUIDField(default=pyuuid.uuid4, editable=False)
    course = models.ForeignKey(Course)
    title = models.CharField(max_length=255)
    subchapters = JSONField(default=tuple())  # Array of strings.
    locator_id = models.CharField(max_length=255)

    def __str__(self):
        return self.title
