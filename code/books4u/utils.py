from .models import *
import re
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.contrib.auth.hashers import check_password, make_password
from django.utils import timezone
from email.mime.multipart import MIMEMultipart
import smtplib
from email.mime.text import MIMEText
import datetime
import os


class EmptyInputError(Exception):
    """Raised when input value is None"""


def check_none(input):
    if input is None or input.isspace() or input == '':
        raise EmptyInputError

    return input


def password_filter(pwd):
    length_check = len(pwd) >= 8
    digit_check = re.search(r"\d", pwd)
    if digit_check is None:
        digit_check = False
    else:
        digit_check = True
    uppercase_check = re.search(r"[A-Z]", pwd)
    if uppercase_check is None:
        uppercase_check = False
    else:
        uppercase_check = True
    pwd_check = (length_check and digit_check and uppercase_check)
    # TODO in sprint 3: Return detailed result
    return pwd_check


def authenticate(e_mail, pwd):
    userlist = User.objects.filter(e_mail=e_mail)  # get user based on his username
    if len(userlist) == 1:  # user not found, return none
        if check_password(pwd, userlist[0].password):  # check password
            return userlist[0]
        else:
            return None
    else:
        userlist2 = User.objects.filter(name=e_mail)  # Login with username instead
        if len(userlist2) == 1:  # user not found, return none
            if check_password(pwd, userlist2[0].password):  # check password
                return userlist2[0]
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


def get_reported_comment(session_key):
    session = Session.objects.filter(session_key=session_key)
    for s in session:
        if is_session_expired(s):
            s.delete()
    if len(session) != 1:
        return None
    else:
        return session[0].get_decoded().get('reported_comment')


def get_vote_review(session_key):
    session = Session.objects.filter(session_key=session_key)
    for s in session:
        if is_session_expired(s):
            s.delete()
    if len(session) != 1:
        return None
    else:
        return session[0].get_decoded().get('vote_review')


def get_user_from_session_key(session_key):
    session = Session.objects.filter(session_key=session_key)
    for s in session:
        if is_session_expired(s):
            s.delete()
    if len(session) != 1:
        return None
    else:
        return User.objects.filter(pk=session[0].get_decoded().get('user_id'))[0]


def get_user_permission_type(user):
    if user.permission == 'banned':
        return 'Banned user'
    if user.permission == 'moderator':
        return 'Moderator'
    return 'Normal user'


def mean(ratings):
    return float(sum(ratings)) / max(len(ratings), 1)


def get_book_rating(book):
    review_list = book.review_set.all()
    total = mean([x.rating for x in review_list])
    return total


def send_email(addr, pwd):
    try:
        gmail = 'books4u.forgot@gmail.com'
        password = 'Books4u123!'
        info = 'Your Books4u account password has been reset'
        tr = 'Your Password has been reset to {}'.format(pwd)
        email = MIMEMultipart()
        e_from = gmail
        e_to = addr
        email['Subject'] = info
        email['From'] = e_from
        email['To'] = e_to
        mes = '<p>{}</p><br>{}<br>'.format(
            str(datetime.datetime.now()), tr)
        text = MIMEText(mes, 'html')
        email.attach(text)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(gmail, password)
        server.sendmail(e_from, e_to, email.as_string())
        server.quit()
    except Exception as e:
        print(e)
        
