from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import auth
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.db import transaction
from datetime import datetime, timedelta
import json
from .models import *
from django.contrib.auth.hashers import make_password
from .utils import *
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib.auth.hashers import make_password

ss = SessionStore()


def get_profile(request):
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
            response_data['user'] = user.name
            response_data['name'] = user.name
            response_data['password'] = user.password
            response_data['e_mail'] = user.e_mail
            response_data['gender'] = user.gender
            response_data['personal_intro'] = user.personal_intro
            response_data['permission'] = get_user_permission_type(user)
            response_data['status'] = 'success'
    return HttpResponse(json.dumps(response_data), content_type="application/json")


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
                response_data['author'] = review.user.e_mail
                response_data['comments'] = list()
                comments_list = review.comment_set.all()
                for c in comments_list:
                    response_data['comments'].append({
                        'index': c.index,
                        'content': c.content,
                        'user': c.user.name,
                        'id': c.id,
                        'modified': c.modified,
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
                response_data['cover_image'] = book.cover_image
                response_data['reviews'] = list()
                review_list = book.review_set.all()
                for r in review_list:
                    response_data['reviews'].append({
                        'user': r.user.name,
                        'content': r.content[:100],
                        'rating': r.rating,
                        'id': r.id,
                        'author': r.user.e_mail
                    })
                response_data['permission'] = get_user_permission_type(user)
                response_data["status"] = 'success'
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def get_books_by_isbn(request):
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
            book_isbn = request.POST.get('isbn')
            if book_isbn is None:
                response_data['status'] = 'fail'
                response_data['reason'] = 'no ISBN'
            else:
                response_data["books"] = list()
                response_data["status"] = 'success'
                book_list = Book.objects.all()
                for b in book_list:
                    if b.ISBN == book_isbn:
                        response_data["books"].append({
                            "id": b.id,
                            "ISBN": b.ISBN,
                            "name": b.name,
                            "author": b.author.name,
                            "publish_date": str(b.publish_date),
                            "edition": b.edition,
                            "publish_firm": b.publish_firm,
                            "cover_image": b.cover_image,
                        })
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def get_books_by_publish_firm(request):
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
            book_publish_firm = request.POST.get('publish_firm')
            if book_publish_firm is None:
                response_data['status'] = 'fail'
                response_data['reason'] = 'no publish firm'
            else:
                response_data["books"] = list()
                response_data["status"] = 'success'
                book_list = Book.objects.all()
                for b in book_list:
                    if b.publish_firm == book_publish_firm:
                        response_data["books"].append({
                            "id": b.id,
                            "ISBN": b.ISBN,
                            "name": b.name,
                            "author": b.author.name,
                            "publish_date": str(b.publish_date),
                            "edition": b.edition,
                            "publish_firm": b.publish_firm,
                            "cover_image": b.cover_image,
                        })
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def get_books_by_author(request):
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
            book_author_name = request.POST.get('author')
            if book_author_name is None:
                response_data['status'] = 'fail'
                response_data['reason'] = 'no author'
            else:
                response_data["books"] = list()
                response_data["status"] = 'success'
                book_list = Book.objects.all()
                for b in book_list:
                    if b.author.name == book_author_name:
                        response_data["books"].append({
                            "id": b.id,
                            "ISBN": b.ISBN,
                            "name": b.name,
                            "author": b.author.name,
                            "publish_date": str(b.publish_date),
                            "edition": b.edition,
                            "publish_firm": b.publish_firm,
                            "cover_image": b.cover_image,
                        })
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
                    "cover_image": b.cover_image,
                })

    return HttpResponse(json.dumps(response_data), content_type="application/json")


def add_review(request):
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
            content = request.POST.get('content', "Empty")
            rating = request.POST.get('rating')
            if rating is None:
                response_data['status'] = 'fail'
                response_data['reason'] = 'no rating'
            else:
                book_id = int(request.POST.get('BookID'))
                try:
                    book = Book.objects.get(pk=book_id)
                except ObjectDoesNotExist:
                    response_data['status'] = 'fail'
                    response_data['reason'] = 'Book does not exist'
                    return HttpResponse(json.dumps(response_data), content_type="application/json")
                response_data['status'] = 'success'
                response_data['user'] = user.name
                Review.objects.create(user=user, content=content, rating=rating, book=book)
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
                publish_firm_ = check_none(request.POST.get('publish_firm'))
                edition_ = check_none(request.POST.get('edition'))
                category_ = check_none(request.POST.get('category'))
                author_ = check_none(request.POST.get('author'))
                cover_image_ = check_none(request.POST.get('cover_image'))
            except EmptyInputError:
                response_data["status"] = 'fail'
                response_data["reason"] = 'missing required field'
                return HttpResponse(json.dumps(response_data), content_type="application/json")

            try:
                publish_date_ = check_none(request.POST.get('publish_date'))
            except EmptyInputError:
                response_data["status"] = 'fail'
                response_data["reason"] = 'date not valid'
                return HttpResponse(json.dumps(response_data), content_type="application/json")
                
            # check if the input book exists
            if len(Book.objects.filter(ISBN=ISBN_)) == 1:
                response_data["status"] = 'fail'
                response_data["reason"] = 'already existed'
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

            try:
                with transaction.atomic():
                    new_book = Book(ISBN=ISBN_, name=name_, publish_date=publish_date_, publish_firm=publish_firm_,
                                    edition=edition_,
                                    author=author_o, cover_image=cover_image_)
                    new_book.save()
            except ValidationError:
                new_book = Book(ISBN=ISBN_, name=name_, publish_date='0001-01-01', publish_firm=publish_firm_,
                                edition=edition_,
                                author=author_o, cover_image=cover_image_)
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
            if user.permission != 'moderator':
                response_data["status"] = 'fail'
                response_data['permission'] = get_user_permission_type(user)
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
            if user.permission != 'moderator':
                response_data["status"] = 'fail'
                response_data['permission'] = get_user_permission_type(user)
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
            if user.permission != 'moderator':
                response_data["status"] = 'fail'
                response_data['permission'] = get_user_permission_type(user)
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
            if user.permission == 'banned':
                response_data["status"] = 'fail'
                response_data['permission'] = get_user_permission_type(user)
                response_data["reason"] = 'permission denied'
                return HttpResponse(json.dumps(response_data), content_type="application/json")
            if is_logged_in(user):
                key = get_session_key_from_user(user)
            else:
                ss.create()
                ss['user_id'] = user.id
                ss.set_expiry(1800)
                key = ss.session_key
                ss.save()
            response_data['status'] = 'success'
            response_data['permission'] = get_user_permission_type(user)
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
        elif User.objects.filter(name=account_name).exists():
            response_data['status'] = 'fail'
            response_data['reason'] = 'existing_username'
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


def rating_display(request):
    response_data = dict()
    session_key = request.POST.get('session_key')
    bookid = request.POST.get('id')
    if session_key is None:
        response_data['status'] = 'fail'
        response_data['reason'] = 'no session key'
    elif bookid is None:
        response_data['status'] = 'fail'
        response_data['reason'] = 'no bookid key'
    else:
        user = get_user_from_session_key(session_key)
        if user is None:
            response_data['status'] = 'fail'
            response_data['reason'] = 'session expired'
        else:
            response_data['reviews'] = list()
            b = Book.objects.get(id=bookid)
            review_list = Review.objects.filter(book=b)
            for r in review_list:
                response_data['reviews'].append({
                    "user": r.user.name,
                    "content": r.content,
                    "rating": r.rating,
                })
            response_data['status'] = 'success'

    return HttpResponse(json.dumps(response_data), content_type="application/json")


def comments_display(request):
    response_data = dict()
    session_key = request.POST.get('session_key')
    reviewid = request.POST.get('id')
    if session_key is None:
        response_data['status'] = 'fail'
        response_data['reason'] = 'no session key'
    elif reviewid is None:
        response_data['status'] = 'fail'
        response_data['reason'] = 'no reviewid'
    else:
        user = get_user_from_session_key(session_key)
        if user is None:
            response_data['status'] = 'fail'
            response_data['reason'] = 'session expired'
        else:
            response_data['comments'] = list()
            currentreview = Review.objects.get(id=reviewid)
            comment_list = Comment.objects.filter(review=currentreview)
            for c in comment_list:
                response_data['comments'].append({
                    "user": c.user.name,
                    "content": c.content,
                    "index": c.index,
                    "id": c.id,
                    "modified": c.modified
                })
            response_data['status'] = 'success'

    return HttpResponse(json.dumps(response_data), content_type="application/json")


def add_comment(request):
    response_data = dict()
    session_key = request.POST.get('session_key')
    review_id = request.POST.get('id')
    content = request.POST.get('content')
    reply_username = request.POST.get('reply')
    user = get_user_from_session_key(session_key)
    if session_key is None:
        response_data['status'] = 'fail'
        response_data['reason'] = 'no session key'
    elif user is None:
        response_data["status"] = 'fail'
        response_data["reason"] = 'session expired'
    elif review_id is None:
        response_data['status'] = 'fail'
        response_data['reason'] = 'no session key'
    elif content is None:
        response_data['status'] = 'fail'
        response_data['reason'] = 'no content key'
    elif content == '':
        response_data['status'] = 'fail'
        response_data['reason'] = 'no content input'
    else:
        try:
            review = Review.objects.get(pk=int(review_id))
            response_data['user'] = user.name
        except ObjectDoesNotExist:
            response_data['status'] = 'fail'
            response_data['reason'] = 'Review does not exist'
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        if reply_username is not None:
            content = '@' + str(reply_username) + content
        response_data['status'] = 'success'
        Comment.objects.create(index=0, review=review, user=user, content=content, modified=False)
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def add_comment_bak(request):
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
            content = request.POST.get('content')
            review_id = int(request.POST.get('id'))
            try:
                review = Review.objects.get(pk=review_id)
            except ObjectDoesNotExist:
                response_data['status'] = 'fail'
                response_data['reason'] = 'Review does not exist'
                return HttpResponse(json.dumps(response_data), content_type="application/json")

            response_data['user'] = user.name
            if content == '':
                response_data['status'] = 'fail'
            else:
                response_data['status'] = 'success'
                Comment.objects.create(index=0, review=review, user=user, content=content, modified=False)
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def vote_display(request):
    response_data = dict()
    session_key = request.POST.get('session_key')
    reviewid = request.POST.get('id')
    if session_key is None:
        response_data['status'] = 'fail'
        response_data['reason'] = 'no session key'
    elif reviewid is None:
        response_data['status'] = 'fail'
        response_data['reason'] = 'no reviewid'
    else:
        user = get_user_from_session_key(session_key)
        if user is None:
            response_data['status'] = 'fail'
            response_data['reason'] = 'session expired'
        else:
            response_data['vote'] = list()
            currentreview = Review.objects.get(id=reviewid)
            votemodellist = Vote.objects.filter(review=currentreview)
            allcount = 0
            for v in votemodellist:
                allcount = allcount + v.count
            response_data['vote'].append(allcount)
            response_data['status'] = 'success'
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def edit_comment(request):
    response_data = dict()
    session_key = request.POST.get('session_key')
    commentid = request.POST.get('id')
    new_content = request.POST.get('content')
    if session_key is None:
        response_data['status'] = 'fail'
        response_data['reason'] = 'no session key'
    elif commentid is None:
        response_data['status'] = 'fail'
        response_data['reason'] = 'no commentid'
    else:
        current_user = get_user_from_session_key(session_key)
        if current_user is None:
            response_data['status'] = 'fail'
            response_data['reason'] = 'session expired'
        else:
            try:
                comment = Comment.objects.get(id=commentid, user=current_user)
            except:
                response_data['status'] = 'fail'
                response_data['reason'] = 'illegal user'
            else:
                comment.content = new_content
                comment.modified = True
                comment.save()
                response_data['status'] = 'success'

    return HttpResponse(json.dumps(response_data), content_type="application/json")


def delete_review_by_id(request):
    response_data = dict()
    session_key = request.POST.get('session_key')
    id = request.POST.get('id')
    if session_key is None:
        response_data['status'] = 'fail'
        response_data['reason'] = 'no session key'
    else:
        current_user = get_user_from_session_key(session_key)
        if current_user is None:
            response_data['status'] = 'fail'
            response_data['reason'] = 'session expired'
        else:
            try:
                review = Review.objects.get(id=id)
            except:
                response_data['status'] = 'fail'
                response_data['permission'] = get_user_permission_type(current_user)
                response_data['reason'] = 'illegal user'
            else:
                review.delete()
                response_data['permission'] = get_user_permission_type(current_user)
                response_data['status'] = 'success'
                response_data['id'] = id

    return HttpResponse(json.dumps(response_data), content_type="application/json")


def set_password(request):
    # initialize an output
    response_data = dict()
    # get the user

    if request.method == "POST":
        session_key = request.POST.get('session_key')
        updated_user = get_user_from_session_key(session_key)
        # get the new password from the request by a post action
        new_password = request.POST.get('NewPassword')
        # get the original password
        old_password = request.POST.get('OldPassword')
        # get the user email
        email = updated_user.e_mail
        new_password_confirm = request.POST.get('NewPassword2')

        if new_password is None:
            response_data['status'] = 'fail'
            response_data['reason'] = 'missing password'
        elif new_password != new_password_confirm:
            response_data['status'] = 'fail'
            response_data['reason'] = 'passwords do not match'
        elif authenticate(email, old_password) is None:
            response_data['status'] = 'fail'
            response_data['reason'] = 'authentication failure'
        else:
            # set the the password
            updated_user.password = make_password(new_password)
            # save the user to the data based
            updated_user.save()
            # get the user's email
            response_data['status'] = 'success'

    else:
        response_data['status'] = 'fail'
        response_data['reason'] = 'request_method'
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def set_gender(request):
    response_data = dict()

    if request.method == "POST":
        # required info for updating name
        session_key = request.POST.get('session_key')
        update_user = get_user_from_session_key(session_key)
        new_gender = request.POST.get('NewGender')
        password = request.POST.get("Password")
        email = update_user.e_mail
        if new_gender is None:
            response_data['status'] = 'fail'
            response_data['reason'] = 'update data missing'
        elif new_gender != "Male" and new_gender != "Female" and new_gender != "Unknown":
            response_data['status'] = 'fail'
            response_data['reason'] = 'invalid input'
        elif password is None:
            response_data['status'] = 'fail'
            response_data['reason'] = 'password required'
        elif authenticate(email, password) is None:
            response_data['status'] = 'fail'
            response_data['reason'] = 'authentication failed'
        else:
            # set the name
            update_user.gender = new_gender
            # save the setting
            update_user.save()
            # verify the setting
            if update_user.gender == new_gender:
                response_data['status'] = 'success'
            else:
                response_data['status'] = 'fail'
                response_data['reason'] = 'Saving failed'
    else:
        response_data['status'] = 'fail'
        response_data['reason'] = 'request_method'

    return HttpResponse(json.dumps(response_data), content_type="application/json")


def set_email(request):
    response_data = dict()

    if request.method == "POST":
        # required info for updating name
        session_key = request.POST.get('session_key')
        update_user = get_user_from_session_key(session_key)
        new_email = request.POST.get('NewEmail')
        password = request.POST.get("Password")
        email = update_user.e_mail

        if new_email is None:
            response_data['status'] = 'fail'
            response_data['reason'] = 'update data missing'
        elif password is None:
            response_data['status'] = 'fail'
            response_data['reason'] = 'password required'
        elif User.objects.filter(e_mail=new_email).exists():
            response_data['status'] = 'fail'
            response_data['reason'] = 'existing_email'
        elif authenticate(email, password) is None:
            response_data['status'] = 'fail'
            response_data['reason'] = 'authentication failed'
        else:
            # set the name
            update_user.e_mail = new_email
            # save the setting
            update_user.save()
            # verify the setting
            if update_user.e_mail == new_email:
                response_data['status'] = 'success'
            else:
                response_data['status'] = 'fail'
                response_data['reason'] = 'Saving failed'
    else:
        response_data['status'] = 'fail'
        response_data['reason'] = 'request_method'

    return HttpResponse(json.dumps(response_data), content_type="application/json")


def set_intro(request):
    response_data = dict()
    if request.method == "POST":
        # required info for updating name
        session_key = request.POST.get('session_key')
        update_user = get_user_from_session_key(session_key)
        new_intro = request.POST.get('NewIntro')
        password = request.POST.get("Password")
        email = update_user.e_mail

        if new_intro is None:
            response_data['status'] = 'fail'
            response_data['reason'] = 'update data missing'
        elif password is None:
            response_data['status'] = 'fail'
            response_data['reason'] = 'password required'
        elif authenticate(email, password) is None:
            response_data['status'] = 'fail'
            response_data['reason'] = 'authentication failed'
        else:
            # set the intro
            update_user.personal_intro = new_intro
            # save the setting
            update_user.save()
            # verify the setting
            if update_user.personal_intro == new_intro:
                response_data['status'] = 'success'
            else:
                response_data['status'] = 'fail'
                response_data['reason'] = 'Saving failed'
    else:
        response_data['status'] = 'fail'
        response_data['reason'] = 'request_method'

    return HttpResponse(json.dumps(response_data), content_type="application/json")


def set_name(request):
    response_data = dict()

    if request.method == "POST":
        session_key = request.POST.get('session_key')
        update_user = get_user_from_session_key(session_key)
        # required info for updating name

        new_name = request.POST.get('NewName')
        password = request.POST.get("Password")
        email = update_user.e_mail

        if new_name is None:
            response_data['status'] = 'fail'
            response_data['reason'] = 'update data missing'
        elif password is None:
            response_data['status'] = 'fail'
            response_data['reason'] = 'password required'
        elif User.objects.filter(name=new_name).exists():
            response_data['status'] = 'fail'
            response_data['reason'] = 'existing_username'
        elif authenticate(email, password) is None:
            response_data['status'] = 'fail'
            response_data['reason'] = 'authentication failure'
        else:
            # set the name
            update_user.name = new_name
            # save the setting
            update_user.save()
            # verify the setting
            if update_user.name == new_name:
                response_data['status'] = 'success'
            else:
                response_data['status'] = 'fail'
                response_data['reason'] = 'Saving failed'
    else:
        response_data['status'] = 'fail'
        response_data['reason'] = 'request_method'

    return HttpResponse(json.dumps(response_data), content_type="application/json")
