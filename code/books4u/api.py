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

def validateRating(Rating):
    if(Rating<=5&Rating>=1):
        return true
    else:
        return false

def Autenticate(Username,Password):
    return 0

def getOverallRating():
    return 0

def getMemberGender(ID):
    return 0

def getMemberPersonalIntro(ID):
    return 0

def getMemberStatus(ID):
    return 0

def getMemberPermission(ID):
    return 0



