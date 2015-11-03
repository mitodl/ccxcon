"""
Models necessary to represent a course catalog.
"""
from django.contrib.auth.models import User
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from jsonfield import JSONField
import uuid as pyuuid

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
    video_url = models.URLField()

    edx_instance = models.URLField(max_length=255)
    instructors = models.ManyToManyField(User)
    live = models.BooleanField(default=False)

    price_per_seat_cents = models.IntegerField(
        null=True, blank=True,
        help_text="Cost of the whole course per seat in cents")

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
    subchapters = JSONField(default=tuple()) # Array of strings.
    locator_id = models.CharField(max_length=255)
    price_per_seat_cents = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.title
