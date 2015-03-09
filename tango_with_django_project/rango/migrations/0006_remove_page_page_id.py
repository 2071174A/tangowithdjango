# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rango', '0005_page_page_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='page',
            name='page_id',
        ),
    ]
