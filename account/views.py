from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from account.models import Account
from api.client import Weibo
from api.sdk.weibo import _http_post
import operator
from functools import reduce


@login_required(login_url='/login/')
def index(request):
    context_dict = {'account': request.user.account,
                    'safe': is_last(request.user)}
    return render(request, 'account/index.html', context_dict)


@login_required(login_url='/login/')
def cancel_douban(request):
    if is_safe(request.user, 'douban'):  # not the last bind thrid
        unbind(request.user, 'douban')
    else:
        request.session.delete()
        request.user.delete()
    if 'douban_token' in request.session:
        del request.session['douban_token']
    return HttpResponseRedirect('/account/')


@login_required(login_url='/login/')
def cancel_weibo(request):
    if is_safe(request.user, 'weibo'):  # not the last bind thrid
        unbind(request.user, 'weibo')
        if 'weibo_token' in request.session:
            token = request.session['weibo_token']
            if _http_post('https://api.weibo.com/oauth2/revokeoauth2',
                          access_token=token)['result'] == 'true':
                del request.session['weibo_token']
    else:
        request.session.delete()
        request.user.delete()
        if 'weibo_token' in request.session:
            token = request.session['weibo_token']
            if _http_post('https://api.weibo.com/oauth2/revokeoauth2',
                          access_token=token)['result'] == 'true':
                del request.session['weibo_token']

    return HttpResponseRedirect('/account/')


@login_required(login_url='/login/')
def cancel_qq(request):
    if is_safe(request.user, 'qq'):  # not the last bind thrid
        unbind(request.user, 'qq')
    else:
        request.session.delete()
        request.user.delete()
    if 'qq_token' in request.session:
        del request.session['qq_token']
    if 'qq_openid' in request.session:
        del request.session['qq_openid']
    return HttpResponseRedirect('/account/')


#-------------------------------------------------------#
def is_last(user):
    dic = {'weibo': user.account.bind_weibo,
           'douban': user.account.bind_douban,
           'qq': user.account.bind_qq}
    return dic.values().count(True) == 1


def is_safe(user, thrid):
    dic = {'weibo': user.account.bind_weibo,
           'douban': user.account.bind_douban,
           'qq': user.account.bind_qq}
    dic[thrid.lower()] = not dic[thrid.lower()]
    return reduce(operator.or_, dic.values())


def is_exist(uid, thrid):
    dic = {'weibo': 'weibo_uid',
           'qq': 'qq_number',
           'douban': 'douban_uid'}
    # to_exec='Account.objects.filter('+dic[thrid.lower()]+'=\''+str(uid)+'\').exists()'
    to_eval = "Account.objects.filter({0}='{1}').exists()".format(
        dic[thrid.lower()], str(uid))
    return eval(to_eval)


def unbind(user, thrid):
    account = user.account
    exec 'account.bind_%s=False' % thrid
    if not thrid == 'qq':
        exec 'account.%s_uid=""' % thrid
    else:
        exec 'account.%s_number=""' % thrid
    account.save()
    delete_oauth(thrid)


def delete_oauth(thrid):
    pass
