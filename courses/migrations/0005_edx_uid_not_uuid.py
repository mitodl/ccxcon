# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0004_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='edxauthor',
            name='edx_uid',
            field=models.CharField(help_text=b'Unique ID generated by the edx-platform', unique=True, max_length=32),
        ),
    ]
