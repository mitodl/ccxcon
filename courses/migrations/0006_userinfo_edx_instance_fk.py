# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-30 14:28
# pylint: skip-file
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('oauth_mgmt', '__first__'),
        ('courses', '0005_rename_edx_instance_fk'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='edx_instance_fk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='oauth_mgmt.BackingInstance'),
        ),
    ]
