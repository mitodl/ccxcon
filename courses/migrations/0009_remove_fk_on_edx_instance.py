# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-30 14:35
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0008_remove_userinfo_edx_instance'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userinfo',
            old_name='edx_instance_fk',
            new_name='edx_instance',
        ),
    ]
