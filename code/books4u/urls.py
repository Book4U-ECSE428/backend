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
    path('rating_display/', api.rating_display),
    path('comments_display/', api.comments_display),
    path('addComment/', api.add_comment),
    path('vote_display/', api.vote_display),
    path('getBookByID/', api.get_book_by_id),
    path('getReviewByID/', api.get_review_by_id),
    path('addReview/', api.add_review),
]
