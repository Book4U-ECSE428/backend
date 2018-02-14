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


def get_review_by_id(request):
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
            response_data['request_user'] = user.name
            review_id = int(request.POST.get('id'))
            if review_id is None:
                response_data['status'] = 'fail'
                response_data['reason'] = 'no book id'
            else:
                try:
                    review = Review.objects.get(pk=review_id)
                except ObjectDoesNotExist:
                    response_data['status'] = 'fail'
                    response_data['reason'] = 'Object does not exist'
                    return HttpResponse(json.dumps(response_data), content_type="application/json")
                response_data['review_user'] = review.user.name
                response_data['review_content'] = review.content
                response_data['review_rating'] = review.rating
                response_data['book_name'] = review.book.name
                response_data['comments'] = list()
                comments_list = review.comment_set.all()
                for c in comments_list:
                    response_data['comments'].append({
                        'index': c.index,
                        'content': c.content,
                        'user': c.user.name,
                        # mock vote value
                        'vote': 100
                    })
                response_data["status"] = 'success'
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def get_book_by_id(request):
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
            response_data['request_user'] = user.name
            book_id = int(request.POST.get('id'))
            if book_id is None:
                response_data['status'] = 'fail'
                response_data['reason'] = 'no book id'
            else:
                try:
                    book = Book.objects.get(pk=book_id)
                except ObjectDoesNotExist:
                    response_data['status'] = 'fail'
                    response_data['reason'] = 'does not exist'
                    return HttpResponse(json.dumps(response_data), content_type="application/json")
                response_data['book_name'] = book.name
                response_data['book_ISBN'] = book.ISBN
                response_data['book_publish_date'] = str(book.publish_date)
                response_data['book_publish_firm'] = book.publish_firm
                response_data['book_edition'] = book.edition
                response_data['book_category'] = book.category.name
                response_data['book_author'] = book.author.name
                response_data['reviews'] = list()
                review_list = book.review_set.all()
                for r in review_list:
                    response_data['reviews'].append({
                        'user': r.user.name,
                        'content': r.content[:100],
                        'rating': r.rating,
                        'id': r.id
                    })
                response_data["status"] = 'success'
    return HttpResponse(json.dumps(response_data), content_type="application/json")


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
                publish_firm_ = check_none(request.POST.get('publish_firm'))
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

            new_book = Book(ISBN=ISBN_, name=name_, publish_date=publish_date_, publish_firm=publish_firm_, edition=edition_,
                            author=author_o)
            new_book.save()
            new_book.category.set([category_o])

            response_data["status"] = 'success'

    return HttpResponse(json.dumps(response_data), content_type="application/json")


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
