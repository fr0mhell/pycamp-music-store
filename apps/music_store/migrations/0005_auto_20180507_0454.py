# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-05-07 04:54
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('music_store', '0004_auto_20180419_0626'),
    ]

    operations = [
        migrations.AlterField(
            model_name='liketrack',
            name='track',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='music_store.Track', verbose_name='track'),
        ),
        migrations.AlterField(
            model_name='liketrack',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to=settings.AUTH_USER_MODEL, verbose_name='liked by'),
        ),
    ]
