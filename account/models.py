from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete, class_prepared

# Create your models here.


class Account(models.Model):
    user = models.OneToOneField(User)  # One2One
    # extends fields
    username = models.CharField(max_length=64, default='')
    # weibo/douban/qq/ avatar url
    avatar_url = models.CharField(max_length=200)
    # Weibo
    bind_weibo = models.BooleanField(default=False)
    weibo_uid = models.CharField(max_length=32, default='')
    # Douban
    bind_douban = models.BooleanField(default=False)
    douban_uid = models.CharField(max_length=32, default='')
    # QQ
    bind_qq = models.BooleanField(default=False)
    qq_number = models.CharField(max_length=64, default='')


def create_account(sender, instance, created, **kw):
    if created:
        Account.objects.create(user=instance)

post_save.connect(create_account, sender=User)


def delete_account(sender, instance, **kw):
    if hasattr(instance, 'account'):
        instance.account.delete()

pre_delete.connect(delete_account, sender=User)


def longer_username(sender, *args, **kwargs):
    if sender.__name__ == "User" and sender.__module__ == "django.contrib.auth.models":
        sender._meta.get_field("username").max_length = 64

# class_prepared.connect(longer_username)
