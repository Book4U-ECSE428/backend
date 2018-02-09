from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import auth
import json
from .models import *
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from datetime import datetime, timedelta
from .utils import *

ss = SessionStore()


def get_all_books(request):
    response_data = dict()
    session_key = request.POST.get('session_key')
    if session_key is None:
        response_data['status'] = 'fail'
        response_data['reason'] = 'no session key'
    else:
        user = get_user_from_session_key(session_key)
        if user is None:
            response_data["status"] = 'fail'
            response_data["reason"] = 'session expired'
        else:
            response_data["books"] = list()
            response_data["user"] = user.name
            response_data["status"] = 'success'
            book_list = Book.objects.all()
            for b in book_list:
                response_data["books"].append({
                    "name": b.name,
                    "author": b.author.name,
                    "publish_date": str(b.publish_date),
                })

    return HttpResponse(json.dumps(response_data), content_type="application/json")


def login(request):
    response_data = dict()
    u_email = request.POST.get("e_mail")
    u_pwd = request.POST.get("password")
    if None not in (u_email, u_pwd):
        user = authenticate(e_mail=u_email, pwd=u_pwd)
        if user is not None:
            if is_logged_in(user):
                key = get_session_key_from_user(user)
            else:
                ss.create()
                ss['user_id'] = user.id
                ss.set_expiry(1800)
                key = ss.session_key
                ss.save()
            response_data['status'] = 'success'
            response_data['session_key'] = key
        else:
            response_data['status'] = 'fail'
            response_data['reason'] = 'no such user'
    else:
        response_data['status'] = 'fail'
        response_data['reason'] = 'missing field'
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def create_account(request):
    response_data = dict()
    if request.method == "POST":
        account_name = request.POST.get('name')
        account_password = request.POST.get('password')
        account_e_mail = request.POST.get('e_mail')
        account_gender = request.POST.get('gender', 'Unknown')
        account_personal_intro = request.POST.get('personal_intro', '')
        if account_name is None:
            response_data['status'] = 'fail'
            response_data['reason'] = 'missing name'
        elif account_e_mail is None:
            response_data['status'] = 'fail'
            response_data['reason'] = 'missing email'
        elif User.objects.filter(e_mail=account_e_mail).exists():
            response_data['status'] = 'fail'
            response_data['reason'] = 'existing_email'
        elif not password_filter(account_password):
            response_data['status'] = 'fail'
            response_data['reason'] = 'pwd_filter_failure'
        else:
            new_user = User(name=account_name, password=account_password, e_mail=account_e_mail, gender=account_gender, personal_intro=account_personal_intro)
            new_user.save()
            if User.objects.filter(e_mail=account_e_mail).exists():
                response_data['status'] = 'success'
            else:
                response_data['status'] = 'fail'
                response_data['reason'] = 'saving failure'
    else:
        response_data['status'] = 'fail'
        response_data['reason'] = 'request_method'
    return HttpResponse(json.dumps(response_data), content_type="application/json")
