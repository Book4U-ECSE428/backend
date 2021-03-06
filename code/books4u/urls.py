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
    path('getProfile/', api.get_profile),
    path('edit_comment/', api.edit_comment),
    path('deleteReviewByID/', api.delete_review_by_id),
    path('setPassword/', api.set_password),
    path('setIntro/', api.set_intro),
    path('setName/', api.set_name),
    path('setEmail/', api.set_email),
    path('setGender/', api.set_gender),
    path('get_books_by_author', api.get_books_by_author),
    path('get_books_by_isbn', api.get_books_by_isbn),
    path('get_books_by_publish_firm', api.get_books_by_publish_firm),
    path('report_comment/', api.report_comment),
    path('vote_like/', api.vote_like),
    path('vote_dislike/', api.vote_dislike),
    path('forgot/', api.forgot_password),
    path('allCategory/', api.get_all_genres),
]
