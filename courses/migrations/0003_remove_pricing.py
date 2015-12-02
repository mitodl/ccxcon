# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0002_add_edx_author_model'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='price_per_seat_cents',
        ),
        migrations.RemoveField(
            model_name='module',
            name='price_per_seat_cents',
        ),
    ]
