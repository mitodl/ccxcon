# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-29 16:32
# pylint: skip-file
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('oauth_mgmt', '__first__'),
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='edx_instance_fk',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='oauth_mgmt.BackingInstance'),
        ),
    ]
