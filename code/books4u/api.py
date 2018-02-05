from django.shortcuts import render
from django.http import HttpResponse
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
            account_password = request.POST.get('password')
            account_e_mail = request.POST.get('e_mail')
            account_gender = request.POST.get('gender')
        except ValueError:
            print("Failed getting request")
        try:
            new_user = User(name=account_name, password=account_password, e_mail=account_e_mail, gender=account_gender)
            new_user.save()
        except(TypeError, ValueError):
            print("Failed saving data")
        return HttpResponse("success")
    else:
        return HttpResponse("failure")

