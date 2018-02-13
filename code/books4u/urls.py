from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from . import api

urlpatterns = [
    path('add_book/', api.add_book),
    path('get_pending_books/', api.get_pending_books),
    path('commit_book/', api.commit_book),
    path('reject_book/', api.reject_book),
    path('getAllBooks/', api.get_all_books),
    path('createAccount/', api.create_account),
    path('login/', api.login),
    path('getBookByID/', api.get_book_by_id),
]
