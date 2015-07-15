# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Third',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', models.BooleanField(default=False)),
                ('username', models.CharField(default=b'', max_length=40)),
                ('avatar_url', models.URLField(default=b'')),
                ('bind_douban', models.BooleanField(default=False)),
                ('douban_uid', models.CharField(default=b'', max_length=40)),
                ('bind_weibo', models.BooleanField(default=False)),
                ('weibo_uid', models.CharField(default=b'', max_length=40)),
                ('bind_qq', models.BooleanField(default=False)),
                ('qq_uid', models.CharField(default=b'', max_length=40)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
