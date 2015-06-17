from django.conf.urls import url, patterns
import views

urlpatterns = patterns('',
                       url(r'^$',
                           views.index,
                           name='account.index'),
                       url(r'^cancel_douban/$',
                           views.cancel_douban,
                           name='account.cancel_douban'),
                       url(r'^cancel_qq/$',
                           views.cancel_qq,
                           name='account.cancel_qq'),
                       url(r'^cancel_weibo/$',
                           views.cancel_weibo,
                           name='account.cancel_weibo'),
                       )
