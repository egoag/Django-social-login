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
            name='Account',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(default=b'', max_length=64)),
                ('avatar_url', models.CharField(max_length=200)),
                ('bind_weibo', models.BooleanField(default=False)),
                ('weibo_uid', models.CharField(default=b'', max_length=32)),
                ('bind_douban', models.BooleanField(default=False)),
                ('douban_uid', models.CharField(default=b'', max_length=32)),
                ('bind_qq', models.BooleanField(default=False)),
                ('qq_number', models.CharField(default=b'', max_length=32)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
