from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import auth
import json
from .models import *
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from datetime import datetime, timedelta

ss = SessionStore()


def get_all_books(request):
    response_data = dict()

    session_key = request.POST.get('session_key')
    if session_key is None:
        response_data['status'] = 'fail'
        response_data['reason'] = 'no session key'
    else:
        se = SessionStore(session_key=session_key)

        response_data["books"] = list()
        response_data["user"] = se['user']
        book_list = Book.objects.all()
        for b in book_list:
            response_data["books"].append({
                "name": b.name,
                "author": b.author.name,
                "publish_date": str(b.publish_date),
            })

    return HttpResponse(json.dumps(response_data), content_type="application/json")


def login(request):
    print(request.POST)
    response_data = dict()
    u_name = request.POST.get("username")
    u_pwd = request.POST.get("password")
    u = User(username='tuser', password='tpwd').save()
    if request.method == "POST":
        user = auth.authenticate(username=u_name, password=u_pwd)
        if user is not None:
            print("authenticated")
            auth.login(request, user)
            print("key {}".format(request.session.sesion_key))
        else:
            print("auth failed")
    # ss.create()
    # # 1800s = 30 mins session expires
    # ss.set_expiry(1800)
    # ss['user'] = request.POST.get('username')
    # ss.save()
    # response_data['status'] = 'success'
    # response_data['session_key'] = ss.session_key
    res = HttpResponse(json.dumps(response_data), content_type="application/json")
    return res


def t(request):
    k = SessionStore(session_key=request.POST.get("key"))
    return HttpResponse(json.dumps({'name': k['user']}), content_type="application/json")
