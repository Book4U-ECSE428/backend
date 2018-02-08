from django.test import TestCase
from django.test import Client
from .models import *
from .utils import *

c = Client()


class ApiTestCase(TestCase):
    def setUp(self):
        User.objects.create(e_mail='michael@example.com', password='Password123')

    def test_create_account(self):
        print("test_create_account success case")
        response = c.post('/api/createAccount/', {'e_mail': '12333@exampe.com', 'password': 'pwd123456'})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        print("test_create_account email taken failure")
        response = c.post('/api/createAccount/', {'e_mail': 'michael@example.com', 'password': 'pwd'})
        response = response.json()
        self.assertEqual("failure", response.get('status'))
        self.assertEqual("existing_email", response.get('detail'))
