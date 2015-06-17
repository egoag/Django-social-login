# -*- coding: UTF-8 -*-
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.conf import settings as st
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, get_user, login
from api.sdk.weibo import APIError as WeiboAPIError
from api.sdk.qq import APIError as QQAPIError
from api.sdk.douban_client.api.error import DoubanAPIError, DoubanOAuthError
from api.client import Weibo, Douban, QQ
from account.models import Account

#
ERROR_CODE = {'bound': 1, }

#


def register(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/account/')
    else:
        return render(request, 'login/index.html', {'page_title': '注册一个新的账号'})


def index(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/account/')
    else:
        return render(request, 'login/index.html', {'page_title': '使用第三方账号登陆'})


def douban_login(request):
    return HttpResponseRedirect(Douban().authorize_url)


def douban_login_complete(request):
    if 'code' in request.GET:
        douban = Douban()
        code = request.GET['code']
        try:
            douban.auth_with_code(code)
        except DoubanOAuthError as e:
            return render(request, 'login/error.html',
                          {'error': e.status, 'msg': e.reason})
        request.session['douban_token'] = douban.token_code
        _get = lambda y, x: y[x] if x in y else None
        me = douban.user.me
        uid = _get(me, 'id')
        name = _get(me, 'name')
        avatar = _get(me, 'avatar')
        return reg_or_bind(request, uid, 'douban', name=name, avatar=avatar)
    else:
        return render(request, 'login/access_denied.html', {})


def weibo_login(request):
    return HttpResponseRedirect(Weibo().get_authorize_url(scope=''))


def weibo_login_complete(request):
    if 'code' in request.GET:
        code = request.GET['code']
        client = Weibo()
        try:
            r = client.request_access_token(code)
        except WeiboAPIError as e:
            return render(request,
                          'login/error.html',
                          {'error': e.error_code,
                           'msg': e.error,
                           'request': e.request})
        token = r.access_token
        expires = r.expires_in
        request.session['weibo_token'] = token
        request.session['weibo_expires'] = expires
        client.set_access_token(token, expires)
        uid = r.uid
        show = client.users.show.get(uid=uid)
        _get = lambda y, x: y[x] if x in y else None
        name = _get(show, 'name')
        avatar = _get(show, 'profile_image_url')
        return reg_or_bind(request, uid, 'weibo', name=name, avatar=avatar)
    else:
        return render(request, 'login/access_denied.html', {})


def qq_login(request):
    return HttpResponseRedirect(QQ().get_authorize_url())


def qq_login_complete(request):
    if 'code' in request.GET:
        code = request.GET['code']
        client = QQ()
        try:
            r = client.request_access_token(code)
        except QQAPIError as e:
            return render(request, 'login/error.html',
                          {'error': e.error_code, 'msg': e.error})
        #r = client.request_access_token(code)
        request.session['qq_token'] = r.access_token
        request.session['qq_expires'] = r.expires_in
        o = client.get_openid(r.access_token)
        openid = o.openid
        request.session['qq_openid'] = openid
        client.set_access_token(access_token=r.access_token,
                                expires=r.expires_in,
                                openid=openid)
        user_info = client.user.get_user_info.get(
            access_token=r.access_token,
            oauth_consumer_key=o.client_id,
            openid=o.openid)
        _get = lambda y, x: y[x] if x in y else None
        uid = openid
        name = _get(user_info, 'nickname')
        avatar = _get(user_info, 'figureurl')
        print '>>>uid', uid
        return reg_or_bind(request, uid, 'qq', name=name, avatar=avatar)
    else:
        return render(request, 'login/access_denied.html', {})


def bound(request):
    return render(request, 'login/bound.html', {})


def access_denied(request):
    return render(request, 'login/access_denied.html', {})
#---------------------------------------------------------------------------------#


def is_bound_by_other(user, uid, thrid):
    dic = {'weibo': 'weibo_uid',
           'qq': 'qq_number',
           'douban': 'douban_uid'}
    # to_exec='Account.objects.filter('+dic[thrid.lower()]+'=\''+str(uid)+'\').exists()'
    # print 'user is',user.account.username
    print 'check bind', thrid
    print 'check uid', uid
    print 'check string', "Account.objects.filter({0}='{1}').exists()".format(dic[thrid.lower()], str(uid))
    exist = eval("Account.objects.filter({0}='{1}').exists()".format(
        dic[thrid.lower()], str(uid)))
    print 'uid exist?', exist
    if hasattr(user, 'account'):
        if exist:
            if user.account == eval("Account.objects.filter({0}='{1}').first()".format(
                    dic[thrid.lower()], str(uid))):
                print 'the uid is bind to this account'
                return False
            else:
                print 'the uid is not bind to this account'
                return True
        return False
    else:
        return exist


def is_existed(uid):
    return User.objects.filter(username=uid).exists()


def is_bound(uid, third):
    dic = {'weibo': 'weibo_uid',
           'qq': 'qq_number',
           'douban': 'douban_uid'}
    return eval("Account.objects.filter({0}='{1}').first()".format(
        dic[third.lower()], str(uid)))


def create_weibo_account(uid, name='', avatar=''):
    user = authenticate(uid=uid)  # must be a new user
    account = user.account
    account.bind_weibo = True
    account.username = name
    account.avatar_url = avatar
    account.weibo_uid = uid
    account.save()
    return account


def create_douban_account(uid, name='', avatar=''):
    user = authenticate(uid=uid)  # must be a new user
    account = user.account
    account.bind_douban = True
    account.username = name
    account.avatar_url = avatar
    account.douban_uid = uid
    account.save()
    return account


def create_qq_account(uid, name='', avatar=''):
    user = authenticate(uid=uid)  # must be a new user
    account = user.account
    account.bind_qq = True
    account.username = name
    account.avatar_url = avatar
    account.qq_number = uid
    account.save()
    return account


def bind_douban_account(user, uid):
    account = user.account
    account.bind_douban = True
    account.douban_uid = uid
    account.save()


def bind_weibo_account(user, uid):
    account = user.account
    account.bind_weibo = True
    account.weibo_uid = uid
    account.save()


def bind_qq_account(user, uid):
    account = user.account
    account.bind_qq = True
    account.qq_number = uid
    account.save()


def reg_or_bind(request, uid, thrid, name='', avatar=''):
    if request.user.is_authenticated():  # login, bind new thrid account
        if not is_bound_by_other(request.user, uid, thrid):
            print 'bind new third account', uid
            to_eval = 'bind_%s_account(request.user,uid)' % thrid.lower()
            eval(to_eval)
            return HttpResponseRedirect('/account/')
        else:
            return HttpResponseRedirect('/login/bound/')
    else:  # loggout or create new
        if not is_existed(uid):  # not is User.username
            account = is_bound(uid, thrid)
            if account:  # in Account.weibo_uid\douban_uid\qq_number
                print 'login bound third account', uid
                print 'user.username', account.user.username
                user = authenticate(uid=account.user.username)
                login(request, user)
                return HttpResponseRedirect('/account/')
            else:  # create new account
                print 'create new account', uid
                to_eval = 'create_%s_account(uid=uid,name=name,avatar=avatar)' % thrid.lower(
                )
                account = eval(to_eval)
                login(request, account.user)
                return HttpResponseRedirect('/account/')
        else:  # login
            print 'login account', uid
            user = authenticate(uid=uid)
            login(request, user)
            return HttpResponseRedirect('/account/')
