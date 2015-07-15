from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete, class_prepared


# Create your models here.
class Third(models.Model):
    user = models.OneToOneField(User)
    # is acitve
    active = models.BooleanField(default=False)
    # third party username
    username = models.CharField(max_length=40, default='')
    # third party avatar url
    avatar_url = models.URLField(default='')
    # douban
    bind_douban = models.BooleanField(default=False)
    douban_uid = models.CharField(max_length=40, default='')
    # weibo
    bind_weibo = models.BooleanField(default=False)
    weibo_uid = models.CharField(max_length=40, default='')
    # qq
    bind_qq = models.BooleanField(default=False)
    qq_uid = models.CharField(max_length=40, default='')

    def __str__(self):
        return self.username

# auto User bind
def create_third(sender, instance, created, **kw):
    if created:
        Third.objects.create(user=instance)

post_save.connect(create_third, sender=User)


def delete_third(sender, instance, **kw):
    if hasattr(instance, 'third'):
        instance.third.delete()

pre_delete.connect(delete_third, sender=User)

