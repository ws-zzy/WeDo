# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2019-05-19 13:54
from __future__ import unicode_literals

import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boards', '0002_topic_views'),
    ]

    operations = [
        migrations.AddField(
            model_name='topic',
            name='photo',
            field=models.ImageField(null=True, storage=django.core.files.storage.FileSystemStorage(location='~/photos'), upload_to=''),
        ),
    ]
