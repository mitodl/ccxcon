# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields
from django.conf import settings
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('title', models.CharField(max_length=255)),
                ('author_name', models.CharField(max_length=255)),
                ('overview', models.TextField()),
                ('description', models.TextField()),
                ('video_url', models.URLField()),
                ('edx_instance', models.URLField(max_length=255)),
                ('live', models.BooleanField(default=False)),
                ('price_per_seat_cents', models.IntegerField(help_text=b'Cost of the whole course per seat in cents', null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('instructors', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('title', models.CharField(max_length=255)),
                ('subchapters', jsonfield.fields.JSONField(default=())),
                ('locator_id', models.CharField(max_length=255)),
                ('price_per_seat_cents', models.IntegerField(null=True, blank=True)),
                ('course', models.ForeignKey(to='courses.Course')),
            ],
        ),
    ]
