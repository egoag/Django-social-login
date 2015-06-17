from django.shortcuts import render
from django.contrib.auth import logout as auth_logout
from django.http import HttpResponseRedirect


def index(request):
    return render(request, 'index.html',{'user':request.user})


def logout(request):
    auth_logout(request)
    return HttpResponseRedirect('/')
