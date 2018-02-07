from django.test import TestCase
from django.test import Client
from .models import *
from .utils import *


# Create your tests here.

c = Client()
import time


class ApiTestCase(TestCase):
    def setUp(self):
        p = Permission.objects.create('Normal')
        User.objects.create(e_mail='n@n.com', password='pwd')
        User.objects.create(e_mail='m@m.com', password='pwd', permissoon=p)

    # TODO will work on it later
    def test_add_book(self):
        pass

    def test_get_pending_books(self):
        pass

    def test_commit_book(self):
        pass

    def test_reject_book(self):
        pass
