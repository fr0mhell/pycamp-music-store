# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-05-04 06:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music_store', '0005_auto_20180507_0454'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentmethod',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
