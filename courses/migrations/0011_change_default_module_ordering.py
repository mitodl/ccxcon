# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-04 20:47
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0010_module_order_field'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='module',
            options={'ordering': ('course_id', 'order')},
        ),
    ]
