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
        account_name = request.POST.get('name')
        if User.objects.filter(name=account_name).exists():
            return HttpResponse(json.dumps({'status': 'failure', 'detail': 'name_taken'}))
        account_password = request.POST.get('password')
        # Password filter can be implemented here
        account_e_mail = request.POST.get('e_mail')
        if User.objects.filter(e_mail=account_e_mail).exists():
            return HttpResponse(json.dumps({'status': 'failure', 'detail': 'existing_email'}))
        account_gender = request.POST.get('gender')
        try:
            new_user = User(name=account_name, password=account_password, e_mail=account_e_mail, gender=account_gender)
            new_user.save()
        except :
            HttpResponse(json.dumps({'status': 'failure', 'detail': 'saving'}))
        return HttpResponse(json.dumps({'status': 'success'}))
    else:
        return HttpResponse(json.dumps({'status': 'failure', 'detail': 'method'}))
