from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import make_password
from django.contrib.auth import check_password
import json
from .models import *

def get_all_books(request):
    response_data = dict()
    response_data["books"] = list()
    book_list = Book.objects.all()
    for b in book_list:
        response_data["books"].append({
            "name": b.name,
            "author": b.author.name,
            "publish_date": str(b.publish_date),
        })

    return HttpResponse(json.dumps(response_data), content_type="application/json")

def create_account(request):
    if request.method == "POST":
        try:
            account_name = request.POST.get('name')
            account_password = make_password(request.POST.get('password'))
            account_e_mail = request.POST.get('e_mail')
            account_gender = request.POST.get('gender')
        except ValueError:
            HttpResponse(json.dumps({'status': 'failure_get'}))
        try:
            new_user = User(name=account_name, password=account_password, e_mail=account_e_mail, gender=account_gender)
            new_user.save()
        except(TypeError, ValueError):
            HttpResponse(json.dumps({'status': 'failure_save'}))
        return HttpResponse(json.dumps({'status': 'success'}))
    else:
        return HttpResponse(json.dumps({'status': 'failure_method'}))

def validate_rating(Rating):
    if(Rating<=5&Rating>=1):
        return True
    else:
        return False

""" verify the user by checking the existence of email and corresponded password
    request contains an email and a plain-text password
"""
def autentiate(request):
    if request.method == "POST":
        try:
            email = request.POST.get('email')
            password = request.POST.get('password')
        except requests.exceptions.RequestException:
            return HttpResponse(json.dumps({'status': 'missing_required_fields'}))

        #check if the user exists
        user = User.objects.all()                        
        for u in User:
            if u.email == email and check_password(password, u.password):
                return HttpResponse(json.dumps({'status': 'user authorized'}))
            
        return HttpResponse(json.dumps({'status': 'incorrected email or password'}))

    else:
        return HttpResponse(json.dumps({'status': 'failure_method'}))

def get_overallR_rating():
    return 0

def get_member_gender(ID):
    return 0

def get_member_personal_intro(ID):
    return 0

def get_member_status(ID):
    return 0

def get_member_permission(ID):
    return 0
