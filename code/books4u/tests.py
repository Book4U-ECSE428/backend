from django.test import TestCase
from django.test import Client
from django.contrib.auth.hashers import make_password, check_password
from .models import *
from .utils import *

# Create your tests here.

c = Client()
import time


class ApiTestCase(TestCase):
    def setUp(self):
        u1 = User.objects.create(e_mail='michael@example.com', password=make_password('Password123'), name='michael')
        User.objects.create(e_mail='t@t.com', password=make_password('pwd')).save()
        permission = Permission.objects.create(name='Normal')
        moderator = User.objects.create(e_mail='m@m.com', password=make_password('pwd'))
        moderator.permission.set([permission])
        category = BookCategory.objects.create(name='test_category_1')
        author = Author.objects.create(name='test_author', summary='t')
        book_c = Book.objects.create(ISBN='123456789-1', name='test_book_pending', publish_date='2018-02-10',
                                     edition='1st edition', author=author)
        book_c.category.set([category])
        book_r = Book.objects.create(ISBN='123456789-2', name='test_book_pending', publish_date='2018-02-10',
                                     edition='1st edition', author=author)
        book_r.category.set([category])
        book_c = Book.objects.create(ISBN='123456789-9', name='book_visible', publish_date='2018-02-10',
                                     edition='1st edition', author=author, visibility=True, id=100)
        book_c.category.set([category])
        review_a = Review.objects.create(user=u1, content='Hello Han mei mei', rating=5, book=book_c)
        review_long = Review.objects.create(user=u1,
                                            content='Da ye, lou shang 322 zhu de shi madongmei jia ba? ma dong shen me? '
                                                    'madongmei, shenme dongmei? madongmei a, mashenme mei?'
                                                    'xing daye ni liang kuai zhe ba, hao lei', rating=5, book=book_c)

    def test_add_book(self):
        print("test_add_book success case")
        response = c.post('/api/login/', {'e_mail': 't@t.com', 'password': 'pwd'})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        session_key = response.get('session_key')
        self.assertEqual(True, len(session_key) > 1)
        response = c.post('/api/add_book/', {'session_key': session_key, 'ISBN': '123456789-0', 'name': 'test_book',
                                             'publish_date': '2018-02-10', 'edition': '1st edition',
                                             'category': 'test_category', 'author': 'test_author'})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        print("test_add_book wrong session key")
        response = c.post('/api/getAllBooks/', {'session_key': "aaaaaaaaa"})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual('session expired', response.get('reason'))
        print("test_add_book no session key")
        response = c.post('/api/getAllBooks/', {})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual('no session key', response.get('reason'))
        print("test_add_book missing field : ISBN")
        response = c.post('/api/add_book/',
                          {'session_key': session_key, 'ISBN': '', 'name': 'test_book', 'publish_date': '2018-02-10',
                           'edition': '1st edition', 'category': 'test_category', 'author': 'test_author'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual('missing required field', response.get('reason'))
        print("test_add_book missing field : name")
        response = c.post('/api/add_book/',
                          {'session_key': session_key, 'ISBN': '123456789-0', 'name': '', 'publish_date': '2018-02-10',
                           'edition': '1st edition', 'category': 'test_category', 'author': 'test_author'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual('missing required field', response.get('reason'))
        print("test_add_book missing field : publish_date")
        response = c.post('/api/add_book/',
                          {'session_key': session_key, 'ISBN': '123456789-0', 'name': 'test_book', 'publish_date': '',
                           'edition': '1st edition', 'category': 'test_category', 'author': 'test_author'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual('missing required field', response.get('reason'))
        print("test_add_book missing field : edition")
        response = c.post('/api/add_book/', {'session_key': session_key, 'ISBN': '123456789-0', 'name': 'test_book',
                                             'publish_date': '2018-02-10', 'edition': '', 'category': 'test_category',
                                             'author': 'test_author'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual('missing required field', response.get('reason'))
        print("test_add_book missing field : category")
        response = c.post('/api/add_book/', {'session_key': session_key, 'ISBN': '123456789-0', 'name': 'test_book',
                                             'publish_date': '2018-02-10', 'edition': '1st edition', 'category': '',
                                             'author': 'test_author'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual('missing required field', response.get('reason'))
        print("test_add_book missing field : author")
        response = c.post('/api/add_book/', {'session_key': session_key, 'ISBN': '123456789-0', 'name': 'test_book',
                                             'publish_date': '2018-02-10', 'edition': '1st edition',
                                             'category': 'test_category', 'author': ''})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual('missing required field', response.get('reason'))

    def test_get_pending_books(self):
        print("test_get_all_book success")
        response = c.post('/api/login/', {'e_mail': 'm@m.com', 'password': 'pwd'})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        session_key = response.get('session_key')
        self.assertEqual(True, len(session_key) > 1)
        response = c.post('/api/get_pending_books/', {'session_key': session_key})
        response = response.json()
        self.assertEqual("123456789-1", response.get("books")[0].get("ISBN"))
        self.assertEqual("123456789-2", response.get("books")[1].get("ISBN"))
        self.assertEqual(2, len(response.get("books")))
        self.assertEqual("success", response.get('status'))
        print("test_get_pending_books wrong session key")
        response = c.post('/api/get_pending_books/', {'session_key': "aaaaaaaaa"})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual('session expired', response.get('reason'))
        print("test_get_pending_books no session key")
        response = c.post('/api/get_pending_books/', {})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual('no session key', response.get('reason'))

    def test_commit_book(self):
        print("test_commit_book success case")
        response = c.post('/api/login/', {'e_mail': 'm@m.com', 'password': 'pwd'})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        session_key = response.get('session_key')
        self.assertEqual(True, len(session_key) > 1)
        response = c.post('/api/commit_book/', {'session_key': session_key, 'ISBN': '123456789-1'})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        print("test_commit_book book does not exist")
        response = c.post('/api/commit_book/', {'session_key': session_key, 'ISBN': '123456789-3'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual('book does not exist', response.get('reason'))
        Session.objects.all()[0].delete()
        print("test_commit_book permission denied")
        response = c.post('/api/login/', {'e_mail': 't@t.com', 'password': 'pwd'})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        session_key = response.get('session_key')
        self.assertEqual(True, len(session_key) > 1)
        response = c.post('/api/commit_book/', {'session_key': session_key, 'ISBN': '123456789-1'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual('permission denied', response.get('reason'))

    def test_reject_book(self):
        print("test_commit_book success case")
        response = c.post('/api/login/', {'e_mail': 'm@m.com', 'password': 'pwd'})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        session_key = response.get('session_key')
        self.assertEqual(True, len(session_key) > 1)
        response = c.post('/api/commit_book/', {'session_key': session_key, 'ISBN': '123456789-2'})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        print("test_commit_book book does not exist")
        response = c.post('/api/commit_book/', {'session_key': session_key, 'ISBN': '123456789-3'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual('book does not exist', response.get('reason'))
        Session.objects.all()[0].delete()
        print("test_commit_book permission denied")
        response = c.post('/api/login/', {'e_mail': 't@t.com', 'password': 'pwd'})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        session_key = response.get('session_key')
        self.assertEqual(True, len(session_key) > 1)
        response = c.post('/api/commit_book/', {'session_key': session_key, 'ISBN': '123456789-2'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual('permission denied', response.get('reason'))

    def test_create_account(self):
        print("test_create_account#1 success case")
        response = c.post('/api/createAccount/',
                          {'e_mail': '12333@exampe.com', 'password': 'PWd123456', 'name': 'Paul'})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        print("test_create_account#2 missing name failure")
        response = c.post('/api/createAccount/', {'e_mail': '123@exampe.com', 'password': 'PWD1123456'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        print("test_create_account#3 email taken failure")
        response = c.post('/api/createAccount/',
                          {'e_mail': 'michael@example.com', 'password': 'ASD123456', 'name': 'm2'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual("existing_email", response.get('reason'))
        print("test_create_account#4 password weak failure")
        response = c.post('/api/createAccount/', {'e_mail': 'asd@example.com', 'password': 's', 'name': 'm2'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))

    def test_login(self):
        print("test_login success case")
        response = c.post('/api/login/', {'e_mail': 't@t.com', 'password': 'pwd'})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        session_key = response.get('session_key')
        print("test_login repeated login within session")
        start_time = time.time()
        for i in range(0, 100):
            # test repeated login within session
            response = c.post('/api/login/', {'e_mail': 't@t.com', 'password': 'pwd'})
            key = response.json().get('session_key')
            self.assertEqual(key, session_key)
        print("test_login 100 requests took %s seconds" % (time.time() - start_time))
        # wrong password case
        print("test_login wrong password case")
        response = c.post('/api/login/', {'e_mail': 't@t.com', 'password': 'aaa'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual("no such user", response.get('reason'))
        # wrong email
        print("test_login wrong email")
        response = c.post('/api/login/', {'e_mail': 't@t.com', 'password': 'aaa'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual("no such user", response.get('reason'))

    def test_get_all_book(self):
        print("test_get_all_book success")
        response = c.post('/api/login/', {'e_mail': 't@t.com', 'password': 'pwd'})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        session_key = response.get('session_key')
        self.assertEqual(True, len(session_key) > 1)
        response = c.post('/api/getAllBooks/', {'session_key': session_key})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        print("test_get_all_book wrong session key")
        response = c.post('/api/getAllBooks/', {'session_key': "aaaaaaaaa"})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual('session expired', response.get('reason'))
        print("test_get_all_book no session key")
        response = c.post('/api/getAllBooks/', {})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual('no session key', response.get('reason'))

    def test_get_book_by_id(self):
        print("test_get_book_by_id")
        response = c.post('/api/login/', {'e_mail': 't@t.com', 'password': 'pwd'})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        session_key = response.get('session_key')
        self.assertEqual(True, len(session_key) > 1)
        print("get book'info")
        response = c.post('/api/getBookByID/', {'session_key': session_key, 'id': 100})
        response = response.json()
        self.assertEqual("book_visible", response.get('book_name'))


class UtilsTestCase(TestCase):
    def setUp(self):
        User.objects.create(e_mail='t@t.com', password=make_password('pwd'))

    def test_pwd_filter(self):
        print("test password filter success")
        result = password_filter("Asd123456")
        self.assertEqual(True, result)
        print("test password filter length failure")
        result = password_filter("Asd16")
        self.assertEqual(False, result)
        print("test password filter upper case failure")
        result = password_filter("ssssssssd16")
        self.assertEqual(False, result)

    def test_authenticate(self):
        print("test_authenticate success")
        u = authenticate(e_mail="t@t.com", pwd='pwd')
        self.assertEqual('t@t.com', u.e_mail)
        self.assertTrue(check_password('pwd', u.password))
        print("test_authenticate fail email")
        u = authenticate(e_mail="aaaaaa@t.com", pwd='pwd')
        self.assertEqual(None, u)
        print("test_authenticate fail pwd")
        u = authenticate(e_mail="t@t.com", pwd='asdfa')
        self.assertEqual(None, u)

    def test_is_logged_in(self):
        print("test_is_logged_in")
        u = authenticate(e_mail="t@t.com", pwd='pwd')
        self.assertFalse(is_logged_in(u))
        response = c.post('/api/login/', {'e_mail': 't@t.com', 'password': 'pwd'})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        self.assertTrue(is_logged_in(u))

    def test_get_session_key_from_user(self):
        print("test_get_session_key_from_user")
        u = authenticate(e_mail="t@t.com", pwd='pwd')
        response = c.post('/api/login/', {'e_mail': 't@t.com', 'password': 'pwd'})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        session_key = response.get('session_key')
        self.assertEqual(session_key, get_session_key_from_user(u))

    def test_get_user_from_session_key(self):
        print("test_get_user_from_session_key")
        response = c.post('/api/login/', {'e_mail': 't@t.com', 'password': 'pwd'})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        session_key = response.get('session_key')
        u = authenticate(e_mail="t@t.com", pwd='pwd')
        self.assertEqual(u, get_user_from_session_key(session_key))

    def test_is_session_expired(self):
        print("test_is_session_expired")
        response = c.post('/api/login/', {'e_mail': 't@t.com', 'password': 'pwd'})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        session_key = response.get('session_key')
        for i in range(0, 100):
            session = Session.objects.get(session_key=session_key)
            self.assertFalse(is_session_expired(session))
