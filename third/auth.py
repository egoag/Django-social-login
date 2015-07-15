from django.contrib.auth.models import User
from django.db.models import Q
from random import choice
from third.models import Third


class ThirdBackend(object):

    '''
    authenticate with uid
    create User whit username = uid,
    password=str([choice[uid] for i in range(len(uid))])
    '''

    def authenticate(self, uid=None, third=None):
        uid = str(uid)
        try:
            # user = User.third.objects.get(username=uid)
            user = Third.objects.get(Q(douban_uid=uid)|Q(weibo_uid=uid)|Q(qq_uid=uid)).user
            return user
        except Third.DoesNotExist:
            user = User(username=uid+third, password=''.join(
                [choice(uid) for i in range(len(uid))]))
            user.set_password(user.password)
            user.save()
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

