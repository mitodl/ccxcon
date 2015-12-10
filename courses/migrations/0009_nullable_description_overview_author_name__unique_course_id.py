# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-16 14:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0008_course_ids_backfilled'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='course_id',
            field=models.TextField(default='wont-exist', help_text=b'course locator from edx', unique=True, null=False),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='course',
            name='author_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='overview',
            field=models.TextField(blank=True, null=True),
        ),
    ]



