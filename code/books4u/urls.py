from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from . import api

urlpatterns = [
    path('getAllBooks/', api.get_all_books),
    path('createAccount/', api.create_account),
    path('login/', api.login),
    path('rating_display/', api.rating_display),
    path('comment_display/', api.comments_display),
]
