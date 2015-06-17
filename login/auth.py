from django.contrib.auth.models import User
from random import choice


class DemoBackend(object):

    '''
    authenticate with uid
    create User whit username = uid,
    password=str([choice[uid] for i in range(len(uid))])
    '''

    def authenticate(self, uid=None):
        uid = str(uid)
        try:
            user = User.objects.get(username=uid)
            return user
        except User.DoesNotExist:
            user = User(username=uid, password=''.join(
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
