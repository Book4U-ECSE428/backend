from .models import *
import re
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.utils import timezone


def password_filter(pwd):

    length_check = len(pwd) > 8
    digit_check = re.search(r"\d", pwd)
    uppercase_check = re.search(r"[A-Z]", pwd)
    pwd_check = (length_check and digit_check and uppercase_check)
    # TODO: Return detailed result
    return pwd_check

def authenticate(e_mail, pwd):
    userlist = User.objects.filter(e_mail=e_mail, password=pwd)  # get user based on his username
    if len(userlist) == 1:  # user not found, return none
        if userlist[0].password == pwd:  # check password
            return userlist[0]
        else:
            return None
    else:
        return None


def is_logged_in(user):
    key = get_session_key_from_user(user)
    return True if key is not None else False


def is_session_expired(session):
    return True if session.expire_date <= timezone.now() else False


def get_session_key_from_user(user):
    ss = Session.objects.all()
    for s in ss:
        u = s.get_decoded().get('user_id')
        if is_session_expired(s):
            s.delete()
        else:
            if u == user.id:
                return s.session_key
    return None


def get_user_from_session_key(session_key):
    session = Session.objects.filter(session_key=session_key)
    for s in session:
        if is_session_expired(s):
            s.delete()
    if len(session) != 1:
        return None
    else:
        return User.objects.filter(pk=session[0].get_decoded().get('user_id'))[0]

