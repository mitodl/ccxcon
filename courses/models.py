"""
Models necessary to represent a course catalog.
"""
import uuid as pyuuid

from django.db import models
from django.contrib.auth.models import User
from django.utils.encoding import python_2_unicode_compatible
from jsonfield import JSONField


@python_2_unicode_compatible
class EdxAuthor(models.Model):
    """
    Represents an author on edX.
    """
    edx_uid = models.CharField(
        max_length=32, unique=True,
        help_text="Unique ID generated by the edx-platform")

    def __repr__(self):
        return "<EdxAuthor edx_uid={}>".format(self.edx_uid)

    def __str__(self):
        return self.edx_uid


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

    def to_webhook(self):
        """
        Webhook serialization
        """
        return {
            'title': self.title,
            'external_pk': str(self.uuid),
        }


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

    def to_webhook(self):
        """
        Webhook serialization
        """
        return {
            'title': self.title,
            'external_pk': str(self.uuid),
            'subchapters': self.subchapters,
            'course_external_pk': self.course.uuid,
        }


@python_2_unicode_compatible
class UserInfo(models.Model):
    """
    Additional information for a given user.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='info')
    edx_instance = models.URLField(max_length=255, blank=True, null=True)

    def __str__(self):
        return "Profile for {}".format(self.user)
