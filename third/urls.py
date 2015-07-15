from django.conf.urls import  url, patterns
from third.views import home, login, register, login_complete, cancel_auth, third_logout

urlpatterns = patterns('',
                       url(r'^$', home, name='third_home'),
                       url(r'^login/$', login, name='third_login'),
                       url(r'^logout/$', third_logout, name='third_logout'),
                       url(r'^login/complete/$', login_complete, name='third_login_complete'),
                       url(r'^register/$', register, name='third_register'),
                       url(r'^cancel-auth/$', cancel_auth, name='third_cancel_auth'),
                       )