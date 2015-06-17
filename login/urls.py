from django.conf.urls import url, patterns
import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='login'),
                       url(r'^weibo/$', views.weibo_login, name='login.weibo'),
                       url(r'^weibo/complete/$', views.weibo_login_complete, name='login.weibo_complete'),
                       url(r'^qq/$', views.qq_login, name='login.qq'),
                       url(r'^qq/complete/$', views.qq_login_complete, name='login.qq_complete'),
                       url(r'^douban/$', views.douban_login, name='login.douban'),
                       url(r'^douban/complete/$', views.douban_login_complete, name='login.douban_complete'),
                       url(r'^bound/$', views.bound, name='login.bound'),
                       url(r'^access_denied/$', views.access_denied, name='login.access_denied'),
                       url(r'^logout/$', 'django.contrib.auth.views.logout')
                       )
