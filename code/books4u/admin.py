# Register your models here.
from django.contrib import admin

from .models import *

admin.site.site_header = admin.site.site_title = admin.site.index_title = 'Books4U'


class UserAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'password',
        'e_mail',
        'gender',
        'personal_intro',
        'status',
    ]


class PermissionAdmin(admin.ModelAdmin):
    list_display = [
        'name',
    ]


class BookCategoryAdmin(admin.ModelAdmin):
    list_display = [
        'name',
    ]


class BookAdmin(admin.ModelAdmin):
    list_display = [
        'ISBN',
        'name',
        'publish_date',
        'publish_firm',
        'edition',
        'visibility',
        'category',
        'author',
    ]


class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        'book',
        'user',
        'content',
        'rating',
    ]


class CommentAdmin(admin.ModelAdmin):
    list_display = [
        'index',
        'review',
        'user',
    ]


class AuthorAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'summary',
    ]


class VoteAdmin(admin.ModelAdmin):
    list_display = [
        'review',
        'user',
    ]


admin.site.register(User, UserAdmin)
admin.site.register(Permission, PermissionAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(BookCategory, BookCategoryAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Vote, VoteAdmin)
