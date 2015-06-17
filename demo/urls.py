from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.shortcuts import render
from login import views as login_views
import views


urlpatterns = patterns('',
    # Examples:
    url(r'^$', views.index, name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/', include('login.urls')),
    url(r'^register/$', login_views.register, name='register'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^account/', include('account.urls')),
)

