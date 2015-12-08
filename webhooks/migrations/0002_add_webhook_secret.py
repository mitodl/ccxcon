# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import webhooks.models


class Migration(migrations.Migration):

    dependencies = [
        ('webhooks', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='webhook',
            name='secret',
            field=models.CharField(default=webhooks.models.get_uuid_hex, max_length=32),
        ),
    ]
