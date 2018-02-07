from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import auth
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from datetime import datetime, timedelta
import json
from .models import *
from .utils import *

""" used by users to add a new book
    visibility of the new book is false, representing not officailly added
"""
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
                return HttpResponse(json.dumps(response_data) content_type="application/json")
                
            #check if the input category exists
            try:
                category_o = BookCategory.objects.get(name == author_)
            except DoesNotExist: #build-in exception raised by get
                category_o = BookCategory(name=category_)
                category_o.save()

            #check if the input author exists
            try:
                author_o = Author.objects.get(name == author_)
            except DoesNotExist:
                author_o = Author(name=author_, summary='')
                author_o.save()
            
            new_book = Book(ISBN=ISBN_, name=name_, publish_date=publish_date_, edition=edition_, category=category_o, author=author_o)
            new_book.save()

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
            if user.permission.name != 'Normal':
                response_data["status"] = 'fail'
                response_data["reason"] = 'permission denied'
            else:
                response_data["books"] = list()
                pending_books = Book.objects.filter(visibility=False)
                for book in pending_books:
                    response_data["books"].append({
                        "name": b.name,
                        "author": b.author.name,
                        "publish_date": str(b.publish_date),
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
            if user.permission.name != 'Normal':
                response_data["status"] = 'fail'
                response_data["reason"] = 'permission denied'
            else:
                try:
                    ISBN_ = check_none(request.POST.get('ISBN'))
                except EmptyInputError:
                    response_data["status"] = 'fail'
                    response_data["reason"] = 'missing required field'
                    return HttpResponse(json.dumps(response_data), content_type="application/json")

                #check if the input book exists
                try:
                    Book.objects.get(ISBN=ISBN_)
                except DoesNotExist: #build-in exception raised by get
                    response_data["status"] = 'fail'
                    response_data["reason"] = 'book does not exist'
                    return HttpResponse(json.dumps(response_data), content_type="application/json")

                #commit the book by setting visibility to true
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
            if user.permission.name != 'Normal':
                response_data["status"] = 'fail'
                response_data["reason"] = 'permission denied'
            else:
                try:
                    ISBN_ = check_none(request.POST.get('ISBN'))
                except EmptyInputError:
                    response_data["status"] = 'fail'
                    response_data["reason"] = 'missing required field'
                    return HttpResponse(json.dumps(response_data), content_type="application/json")

                #check if the input book exists
                try:
                    Book.objects.get(ISBN=ISBN_)
                except DoesNotExist: #build-in exception raised by get
                    response_data["status"] = 'fail'
                    response_data["reason"] = 'book does not exist'
                    return HttpResponse(json.dumps(response_data), content_type="application/json")
            
                #reject a book by deleting it
                Book.objects.get(ISBN=ISBN_).delete()
                return HttpResponse(json.dumps({'status': 'success'}))
    return HttpResponse(json.dumps(response_data), content_type="application/json")
