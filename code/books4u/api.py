from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import auth
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from datetime import datetime, timedelta
import json
from .models import *
from django.contrib.auth.hashers import make_password
from .utils import *
from django.core.exceptions import ObjectDoesNotExist

ss = SessionStore()

""" used by users to add a new book
    visibility of the new book is false, representing not officailly added
"""


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
                    "id": b.id,
                    "name": b.name,
                    "author": b.author.name,
                    "publish_date": str(b.publish_date),
                    "rating": "5",  # TODO: book.rating?
                    "edition": b.edition,
                    "publish_firm": b.publish_firm,

                })

    return HttpResponse(json.dumps(response_data), content_type="application/json")


def add_book(request):
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
            response_data["user"] = user.name
            try:
                ISBN_ = check_none(request.POST.get('ISBN'))
                name_ = check_none(request.POST.get('name'))
                publish_date_ = check_none(request.POST.get('publish_date'))
                edition_ = check_none(request.POST.get('edition'))
                category_ = check_none(request.POST.get('category'))
                author_ = check_none(request.POST.get('author'))
            except EmptyInputError:
                response_data["status"] = 'fail'
                response_data["reason"] = 'missing required field'
                return HttpResponse(json.dumps(response_data), content_type="application/json")

            # check if the input category exists
            try:
                category_o = BookCategory.objects.get(name=author_)
            except ObjectDoesNotExist:  # build-in exception raised by get
                category_o = BookCategory(name=category_)
                category_o.save()

            # check if the input author exists
            try:
                author_o = Author.objects.get(name=author_)
            except ObjectDoesNotExist:
                author_o = Author(name=author_, summary='')
                author_o.save()

            new_book = Book(ISBN=ISBN_, name=name_, publish_date=publish_date_, edition=edition_,
                            author=author_o)
            new_book.save()
            new_book.category.set([category_o])

            response_data["status"] = 'success'

    return HttpResponse(json.dumps(response_data), content_type="application/json")


""" get books waiting for verification
"""


def get_pending_books(request):
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
            response_data["user"] = user.name
            try:
                p = user.permission.get(name='Normal')
            except ObjectDoesNotExist:
                response_data["status"] = 'fail'
                response_data["reason"] = 'permission denied'
                return HttpResponse(json.dumps(response_data), content_type="application/json")
            response_data["books"] = list()
            pending_books = Book.objects.filter(visibility=False)
            for book in pending_books:
                response_data["books"].append({
                    "ISBN": book.ISBN,
                    "name": book.name,
                    "author": book.author.name,
                    "publish_date": str(book.publish_date),
                    "edition": book.edition,
                    "publish_firm": book.publish_firm
                })
            response_data["status"] = 'success'

    return HttpResponse(json.dumps(response_data), content_type="application/json")


""" commit a pending book by a moderator
"""


def commit_book(request):
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
            response_data["user"] = user.name
            try:
                p = user.permission.get(name='Normal')
            except ObjectDoesNotExist:
                response_data["status"] = 'fail'
                response_data["reason"] = 'permission denied'
                return HttpResponse(json.dumps(response_data), content_type="application/json")
        
            try:
                ISBN_ = check_none(request.POST.get('ISBN'))
            except EmptyInputError:
                response_data["status"] = 'fail'
                response_data["reason"] = 'missing required field'
                return HttpResponse(json.dumps(response_data), content_type="application/json")

            # check if the input book exists
            try:
                Book.objects.get(ISBN=ISBN_)
            except ObjectDoesNotExist:  # build-in exception raised by get
                response_data["status"] = 'fail'
                response_data["reason"] = 'book does not exist'
                return HttpResponse(json.dumps(response_data), content_type="application/json")

            # commit the book by setting visibility to true
            Book.objects.get(ISBN=ISBN_).visibility = True
            response_data["status"] = 'success'

    return HttpResponse(json.dumps(response_data), content_type="application/json")


"""reject and remove a pending book by a moderator
"""


def reject_book(request):
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
            response_data["user"] = user.name
            try:
                p = user.permission.get(name='Normal')
            except ObjectDoesNotExist:
                response_data["status"] = 'fail'
                response_data["reason"] = 'permission denied'
                return HttpResponse(json.dumps(response_data), content_type="application/json")
            
            try:
                ISBN_ = check_none(request.POST.get('ISBN'))
            except EmptyInputError:
                response_data["status"] = 'fail'
                response_data["reason"] = 'missing required field'
                return HttpResponse(json.dumps(response_data), content_type="application/json")

            # check if the input book exists
            try:
                Book.objects.get(ISBN=ISBN_)
            except ObjectDoesNotExist:  # build-in exception raised by get
                response_data["status"] = 'fail'
                response_data["reason"] = 'book does not exist'
                return HttpResponse(json.dumps(response_data), content_type="application/json")

            # reject a book by deleting it
            Book.objects.get(ISBN=ISBN_).delete()
            response_data["status"] = 'success'

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

def rating_display(request):
    response_data = dict()
    session_key = request.POST.get('session_key')
    isbn = request.POST.get('ISBN')
    if session_key is None:
        response_data['status'] = 'fail'
        response_data['reason'] = 'no session key'
    elif isbn is None:
        response_data['status'] = 'fail'
        response_data['reason'] = 'no ISBN key'
    else:
        user = get_user_from_session_key(session_key)
        if user is None:
            response_data['status'] = 'fail'
            response_data['reason'] = 'session expired'
        else:
            response_data['reviews'] = list()
            b = Book.objects.get(ISBN=isbn)
            review_list = Review.objects.filter(book=b)
            for r in review_list:
                response_data['reviews'].append({
                    "user":r.user.name,
                    "content": r.content,
                    "rating": r.rating,
                })
            response_data['status'] = 'success'
            
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def comments_display(request):
    response_data = dict()
    session_key = request.POST.get('session_key')
    request_review = request.POST.get('Review')
    if session_key is None:
        response_data['status'] = 'fail'
        response_data['reason'] = 'no session key'
    elif request_review is None:
        response_data['status'] = 'fail'
        response_data['reason'] = 'no review requested'
    else:
        user = get_user_from_session_key(session_key)
        if user is None:
            response_data['status'] = 'fail'
            response_data['reason'] = 'session expired'
        else:
            response_data['comments'] = list()
            comment_list = Comment.objects.filter(review=request_review)
            for c in comment_list:
                response_data['comments'].append({
                    "user": c.user.name,
                    "content": c.content,
                    "index": c.index,
                })
            response_data['status'] = 'success'

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
            new_user = User(name=account_name, password=make_password(account_password), e_mail=account_e_mail,
                            gender=account_gender, personal_intro=account_personal_intro)
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

def update_comment(request):
    response_data = dict()
    session_key = request.POST.get('session_key')
    request_review = request.POST.get('Review')
    new_content = request.POST.get('content')
    if session_key is None:
        response_data['status'] = 'fail'
        response_data['reason'] = 'no session key'
    elif request_review is None:
        response_data['status'] = 'fail'
        response_data['reason'] = 'no review requested'
    else:
        logged_user = get_user_from_session_key(session_key)
        if logged_user is None:
            response_data['status'] = 'fail'
            response_data['reason'] = 'session expired'
        else:
            try:
                comment = Comment.objects.get(review=request_review, user=logged_user)
            except:
                response_data['status'] = 'fail'
                response_data['reason'] = 'comment does not exist'
            else:
                comment.content = new_content
                comment.save()
                response_data['status'] = 'success'
            
    return HttpResponse(json.dumps(response_data), content_type="application/json")
    