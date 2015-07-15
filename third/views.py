# -*- coding: UTF-8 -*-
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.conf import settings as st
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
import operator
from sdk.weibo import APIError as WeiboAPIError
from sdk.qq import APIError as QQAPIError
from douban_client.api.error import DoubanAPIError, DoubanOAuthError
from sdk.weibo import _http_post
from client import Weibo, Douban, QQ
from third.models import Third


@login_required()
def home(request):
    return render(request, 'third/index.html', {'page_title': u'已绑定的第三方账号'})


def register(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('third_home'))
    else:
        return render(request, 'third/register.html', {'page_title': u'以第三方账号注册'})


def login(request):  # redirect page, go to third party authorize page
    third_type = request.GET.get('type')
    if not third_type:
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('third_home'))
        else:
            return render(request, 'third/register.html', {'page_title':u'以第三方账号登陆'})
    third_type = third_type.lower()
    if third_type == 'douban':
        return HttpResponseRedirect(Douban().authorize_url)
    elif third_type == 'weibo':
        return HttpResponseRedirect(Weibo().get_authorize_url(scope=st.WEIBO_SCOPE))
    elif third_type == 'qq':
        return HttpResponseRedirect(QQ().get_authorize_url(scope=st.QQ_SCOPE))
    else:
        return render(request, 'third/error.html', {'msg':'unknown third party login type '})


def login_complete(request):  # redirect page, authencate authorize and go to third home page
    third_type = request.GET.get('type')
    code = request.GET.get('code')
    _get = lambda y, x: y[x] if x in y else None
    if not code:
        return render(request,'third/error.html', {'msg':'login failed.'})
    else:
        if third_type == 'douban':
            print '>>> login_complete type:',third_type
            client = Douban()
            try:
                client.auth_with_code(code)
            except DoubanOAuthError as e:
                return render(request, 'third/error.html', {'errcode':e.status,'msg':e.reason})
            token = client.token_code
            request.session['douban_token'] = token
            try:
                me = client.user.me
            except DoubanAPIError as e:
                return render(request, 'third/error.html', {'errcode':e.status,'msg':e.reason})
            uid = _get(me, 'id')
            name = _get(me, 'name')
            avatar = _get(me, 'avatar')
            return reg_or_bind(request, uid, third_type, name=name, avatar=avatar)
        elif third_type == 'weibo':
            print '>>> login_complete type:',third_type
            client = Weibo()
            try:
                r = client.request_access_token(code)
            except WeiboAPIError as e:
                return render(request, 'third/error.html', {'errcode': e.error_code,'msg': e.error,'request': e.request})
            token = r.access_token
            expires = r.expires_in
            request.session['weibo_token'] = token
            request.session['weibo_expires'] = expires
            client.set_access_token(token, expires)
            uid = r.uid
            try:
                show = client.users.show.get(uid=uid)
            except WeiboAPIError as e:
                return render(request, 'third/error.html', {'errcode':e.error_code,'msg':e.error,'request':e.request})
            name = _get(show, 'name')
            avatar = _get(show, 'profile_image_url')
            return reg_or_bind(request, uid, third_type, name=name, avatar=avatar)
        elif third_type == 'qq':
            print '>>> login_complete type:',third_type
            client = QQ()
            try:
                r = client.request_access_token(code)
            except QQAPIError as e:
                return  render(request, 'third/error.html', {'errcode':e.error_code,'msg':e.error})
            token = r.access_token
            expires = r.expires_in
            try:
                o = client.get_openid(token)
            except QQAPIError as e:
                return  render(request, 'third/error.html', {'errcode':e.error_code,'msg':e.error})
            openid = o.openid
            client_id = o.client_id
            request.session['qq_token'] = token
            request.session['qq_expires'] = expires
            request.session['qq_openid'] = openid
            request.session['qq_client_id'] = client_id
            client.set_access_token(access_token=token, expires=expires, openid=openid)
            try:
                user_info = client.user.get_user_info.get(access_token=token, oauth_consumer_key=client_id,
                                                          openid=openid)
            except QQAPIError as e:
                return  render(request, 'third/error.html', {'errcode':e.error_code,'msg':e.error})
            uid = openid
            name = _get(user_info, 'nickname')
            avatar = _get(user_info, 'figureurl')
            return reg_or_bind(request, uid, third_type, name=name, avatar=avatar)
        else :
            return render(request, 'third/error.html', {'msg':'unsupported third site.'})


def third_logout(request):
    logout(request)
    return HttpResponseRedirect('/')

@login_required()
def cancel_auth(request):
    '''
    check whether the third party oauth is the last, if yes delete user
    :param request:
    :return:
    '''
    if 'type' in request.GET:  # logged in user cancel authorize
        third = request.GET.get('type').lower()
    elif 'uid' in request.GET:  # weibo user manual cancel authorize from weibo
        if request.user.third.weibo_uid == request.GET['uid']:
            third = 'weibo'
        else:
            return render(request, 'third/error.html', {'msg':u'请登录后解除绑定'})
    safe = is_safe(request.user, third)
    if safe:  # this third party authorize is not the only one
        print '>>> cancel is safe'
        try:
            cancel_third_auth(request.session, third)
        except (WeiboAPIError, QQAPIError, DoubanAPIError) as e:
            pass
        exec 'request.user.third.bind_%s=False' % third
        exec 'request.user.third.%s_uid=""' % third
        request.user.third.save()
        clean_user_session(request.session, third)
        return render(request, 'third/index.html', {'error':False, 'msg':u'取消绑定成功'})
    else:  # this thrid party authorize is the only one, delete user.third
        print '>>> cancel %s is not safe'%third
        try:
            cancel_third_auth(request.session, third)
        except (WeiboAPIError, QQAPIError, DoubanAPIError) as e:
            pass
            # if hasattr(e, 'msg'):
            #     msg = e.msg
            # elif hasattr(e, 'error'):
            #     msg = e.error
            # else:
            #     msg = '反认证失败'
            # return render(request, 'third/index.html', {'error':True, 'msg':msg})
        # request.user.third.delete()
        exec 'request.user.third.bind_%s=False' % third
        exec 'request.user.third.%s_uid=""' % third
        request.user.third.active = False  # disactive third after unbound last authorize
        request.user.third.save()
        request.session.delete()
        clean_user_session(request.session, third)
        logout(request)
        return HttpResponseRedirect('/')



def clean_user_session(session, third):
    # clean user message in session
    if third+'_token' in session:
        del session[third+'_token']
    if third+'_expires' in session:
        del session[third+'_expires']
    if third+'_openid' in session:
        del session[third+'_openid']
    if third+'_client_id' in session:
        del session[third+'_client_id']


def cancel_third_auth(session, third):
    if third+'_token' in session:
        token = session[third+'_token']
    else:
        return True  # no token found
    if third == 'weibo':
        _http_post('https://api.weibo.com/oauth2/revokeoauth2',
                      access_token=token)
    else:  # other third party not support cancel oauth
        return True


def reg_or_bind(request, uid, third, name='', avatar=''):
    if request.user.is_authenticated():  # logged in, bind new thrid third party account
        if not is_bound_by_other(request.user, uid, third):  # this uid is not bound by others
            print third,'bind to user'
            bind_third(request.user, uid, third)
            return HttpResponseRedirect(reverse('third_home'))
        else:  # this uid is bound by others
            return render(request, 'third/error.html', {'msg':u'这个账号已经被其他其他账号绑定过了'})
    else:  # login or create new third party account
        if is_registered(uid, third):  # login
            user = authenticate(uid=uid, third=third)
            auth_login(request, user)
            request.user.third.active = True  #whatever, active third
            return HttpResponseRedirect(reverse('third_home'))
        else:  # create new third party account
            user = authenticate(uid=uid, third=third)  # create new user
            third = create_third(user=user, uid=uid,_third=third,name=name, avatar=avatar)
            auth_login(request,user)
            request.user.third.active = True  #whatever, active third
            return HttpResponseRedirect(reverse('third_home'))


def is_bound_by_other(user, uid, third):
    dic = {'weibo': 'weibo_uid',
           'qq': 'qq_uid',
           'douban': 'douban_uid'}
    exist = eval("Third.objects.filter({0}='{1}').exists()".format(
        dic[third.lower()], str(uid)))
    if exist:  # uid exist
        if hasattr(user, 'third'):
            if not user.third == eval("Third.objects.filter({0}='{1}').first()".format(
                    dic[third.lower()], str(uid))):   # uid is bound to itself
                return True
    return False


def is_registered(uid,third):
    dic = {'weibo': 'weibo_uid',
           'qq': 'qq_uid',
           'douban': 'douban_uid'}
    return eval("Third.objects.filter({0}='{1}').exists()".format(
        dic[third.lower()], str(uid)))


def create_third(user, uid, _third, name='', avatar=''):
    third = user.third
    if _third == 'douban':
        third.bind_douban = True
        third.douban_uid = uid
    elif _third == 'weibo':
        third.bind_weibo = True
        third.weibo_uid = uid
    elif _third == 'qq':
        third.bind_qq = True
        third.qq_uid = uid
    else:
        raise NameError
    third.avatar_url = avatar
    third.username = name
    user.third.active = True  # active third
    third.save()

    print '>>>Success: create third object',third
    return third

def bind_third(user, uid, _third):
    third = user.third
    if _third == 'douban':
        third.douban_uid = uid
        third.bind_douban = True
    elif _third == 'weibo':
        third.weibo_uid = uid
        third.bind_weibo = True
    elif _third == 'qq':
        third.qq_uid = uid
        third.bind_qq = True
    else:
        raise NameError
    user.third.active = True  # active third
    third.save()


def is_safe(user, thrid):
    bind_dict = {'weibo': user.third.bind_weibo,
           'douban': user.third.bind_douban,
           'qq': user.third.bind_qq}
    bind_dict[thrid.lower()] = not bind_dict[thrid.lower()]
    return reduce(operator.or_, bind_dict.values())