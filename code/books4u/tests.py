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
        permission_m = 'moderator'
        permission_b = 'banned'
        moderator = User.objects.create(e_mail='m@m.com', password=make_password('pwd'))
        moderator.permission = permission_m
        banned_user = User.objects.create(e_mail='b@b.com', password=make_password('pwd'))
        banned_user.permission = permission_b
        moderator.save()
        banned_user.save()
        category = BookCategory.objects.create(name='test_category_1')
        author = Author.objects.create(name='test_author', summary='t')
        book_c = Book.objects.create(ISBN='123456789-1', name='test_book_pending', publish_date='2018-02-10',
                                     publish_firm='test_firm',
                                     edition='1st edition', author=author)
        book_c.category.set([category])
        book_r = Book.objects.create(ISBN='123456789-2', name='test_book_pending', publish_date='2018-02-10',
                                     publish_firm='test_firm',
                                     edition='1st edition', author=author)
        book_r.category.set([category])
        book_c = Book.objects.create(ISBN='123456789-9', name='book_visible', publish_date='2018-02-10',
                                     publish_firm='test_firm',
                                     edition='1st edition', author=author, visibility=True, id=100)
        book_c.category.set([category])
        review_a = Review.objects.create(user=u1, content='Hello Han mei mei', rating=5, book=book_c, id=1001)
        review_long = Review.objects.create(user=u1,
                                            content='Da ye, lou shang 322 zhu de shi madongmei jia ba? ma dong shen me? '
                                                    'madongmei, shenme dongmei? madongmei a, mashenme mei?'
                                                    'xing daye ni liang kuai zhe ba, hao lei', rating=5, book=book_c)

        comment_a = Comment.objects.create(index=1, review=review_a, user=u1, content='comment!!!!', id=10011)
        review_b = Review.objects.create(user=u1, content='verygood', rating=5, book=book_c, id=101)
        comment_b = Comment.objects.create(index=1, review=review_b, user=u1, content="Your review is very good")
        review_c = Review.objects.create(user=u1, content='verygood', rating=5, book=book_c, id=999)

    def test_add_book(self):
        print("test_add_book success case")
        response = c.post('/api/login/', {'e_mail': 't@t.com', 'password': 'pwd'})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        session_key = response.get('session_key')
        self.assertEqual(True, len(session_key) > 1)
        response = c.post('/api/add_book/', {'session_key': session_key, 'ISBN': '123456789-8', 'name': 'test_book',
                                             'publish_date': '2018-02-10', 'publish_firm': 'test_firm',
                                             'edition': '1st edition',
                                             'category': 'test_category', 'author': 'test_author',
                                             'cover_image': 'https://vignette.wikia.nocookie.net/arthur/images/a/a7/No_Image.jpg/revision/latest?cb=20130610195200'})
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
                           'publish_firm': 'test_firm',
                           'edition': '1st edition', 'category': 'test_category', 'author': 'test_author'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual('missing required field', response.get('reason'))
        print("test_add_book missing field : name")
        response = c.post('/api/add_book/',
                          {'session_key': session_key, 'ISBN': '123456789-0', 'name': '', 'publish_date': '2018-02-10',
                           'publish_firm': 'test_firm',
                           'edition': '1st edition', 'category': 'test_category', 'author': 'test_author',
                           'cover_image': 'https://vignette.wikia.nocookie.net/arthur/images/a/a7/No_Image.jpg/revision/latest?cb=20130610195200'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual('missing required field', response.get('reason'))
        print("test_add_book missing field : publish_date")
        response = c.post('/api/add_book/',
                          {'session_key': session_key, 'ISBN': '123456789-0', 'name': 'test_book', 'publish_date': '',
                           'publish_firm': 'test_firm',
                           'edition': '1st edition', 'category': 'test_category', 'author': 'test_author',
                           'cover_image': 'https://vignette.wikia.nocookie.net/arthur/images/a/a7/No_Image.jpg/revision/latest?cb=20130610195200'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual('date not valid', response.get('reason'))
        print("test_add_book missing field : publish_firm")
        response = c.post('/api/add_book/',
                          {'session_key': session_key, 'ISBN': '123456789-0', 'name': 'test_book',
                           'publish_date': '2018-02-10', 'publish_firm': '',
                           'edition': '1st edition', 'category': 'test_category', 'author': 'test_author',
                           'cover_image': 'https://vignette.wikia.nocookie.net/arthur/images/a/a7/No_Image.jpg/revision/latest?cb=20130610195200'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual('missing required field', response.get('reason'))
        print("test_add_book missing field : edition")
        response = c.post('/api/add_book/',
                          {'session_key': session_key, 'ISBN': '123456789-0', 'name': 'test_book',
                           'publish_date': '2018-02-10', 'publish_firm': 'test_firm',
                           'edition': '', 'category': 'test_category', 'author': 'test_author',
                           'cover_image': 'https://vignette.wikia.nocookie.net/arthur/images/a/a7/No_Image.jpg/revision/latest?cb=20130610195200'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual('missing required field', response.get('reason'))
        print("test_add_book missing field : category")
        response = c.post('/api/add_book/',
                          {'session_key': session_key, 'ISBN': '123456789-0', 'name': 'test_book',
                           'publish_date': '2018-02-10', 'publish_firm': 'test_firm',
                           'edition': '1st edition', 'category': '', 'author': 'test_author',
                           'cover_image': 'https://vignette.wikia.nocookie.net/arthur/images/a/a7/No_Image.jpg/revision/latest?cb=20130610195200'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual('missing required field', response.get('reason'))
        print("test_add_book missing field : author")
        response = c.post('/api/add_book/',
                          {'session_key': session_key, 'ISBN': '123456789-0', 'name': 'test_book',
                           'publish_date': '2018-02-10', 'publish_firm': 'test_firm',
                           'edition': '1st edition', 'category': 'test_category', 'author': '',
                           'cover_image': 'https://vignette.wikia.nocookie.net/arthur/images/a/a7/No_Image.jpg/revision/latest?cb=20130610195200'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual('missing required field', response.get('reason'))
        print("test_add_book missing field : cover_image")
        response = c.post('/api/add_book/',
                          {'session_key': session_key, 'ISBN': '123456789-0', 'name': 'test_book',
                           'publish_date': '2018-02-10', 'publish_firm': 'test_firm',
                           'edition': '1st edition', 'category': 'test_category', 'author': '', 'cover_image': ''})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual('missing required field', response.get('reason'))
        print("test_add_book missing field : publish_date")
        response = c.post('/api/add_book/',
                          {'session_key': session_key, 'ISBN': '123456789-0', 'name': 'test_book', 'publish_date': '',
                           'publish_firm': 'test_firm',
                           'edition': '1st edition', 'category': 'test_category', 'author': 'test_author'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual('missing required field', response.get('reason'))

        print("test_add_book existed book")
        response = c.post('/api/add_book/',
                          {'session_key': session_key, 'ISBN': '123456789-9', 'name': 'test_book',
                           'publish_date': '2018-02-10', 'publish_firm': 'test_firm',
                           'edition': '1st edition', 'category': 'test_category', 'author': 'test_author',
                           'cover_image': 'aaa'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual('already existed', response.get('reason'))

        print("test_add_book invalid date : publish_date")
        response = c.post('/api/add_book/',
                          {'session_key': session_key, 'ISBN': '123456789-0', 'name': 'test_book',
                           'publish_date': 'yahaha', 'publish_firm': 'test_firm',
                           'edition': '1st edition', 'category': 'test_category', 'author': 'test_author',
                           'cover_image': 'aaa'})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        self.assertEqual('0001-01-01', str(Book.objects.get(ISBN='123456789-0').publish_date))

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
        Session.objects.all()[0].delete()
        print("test_get_pending_books permission denied")
        response = c.post('/api/login/', {'e_mail': 't@t.com', 'password': 'pwd'})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        session_key = response.get('session_key')
        self.assertEqual(True, len(session_key) > 1)
        response = c.post('/api/get_pending_books/', {'session_key': session_key, 'ISBN': '123456789-2'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual("Normal user", response.get('permission'))
        self.assertEqual('permission denied', response.get('reason'))

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
        self.assertEqual("Normal user", response.get('permission'))
        self.assertEqual('permission denied', response.get('reason'))

    def test_reject_book(self):
        print("test_commit_book success case")
        response = c.post('/api/login/', {'e_mail': 'm@m.com', 'password': 'pwd'})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        session_key = response.get('session_key')
        self.assertEqual(True, len(session_key) > 1)
        response = c.post('/api/reject_book/', {'session_key': session_key, 'ISBN': '123456789-2'})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        print("test_commit_book book does not exist")
        response = c.post('/api/reject_book/', {'session_key': session_key, 'ISBN': '123456789-3'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual('book does not exist', response.get('reason'))
        Session.objects.all()[0].delete()
        print("test_reject_book permission denied")
        response = c.post('/api/login/', {'e_mail': 't@t.com', 'password': 'pwd'})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        session_key = response.get('session_key')
        self.assertEqual(True, len(session_key) > 1)
        response = c.post('/api/reject_book/', {'session_key': session_key, 'ISBN': '123456789-2'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual("Normal user", response.get('permission'))
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
        self.assertEqual("Normal user", response.get('permission'))
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
        Session.objects.all()[0].delete()
        print("test_login blocked user")
        response = c.post('/api/login/', {'e_mail': 'b@b.com', 'password': 'pwd'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual("Banned user", response.get('permission'))
        self.assertEqual("permission denied", response.get('reason'))

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
        # response = c.post('/api/getBookByID/', {'session_key': session_key, 'id': 100})
        # response = response.json()
        # self.assertEqual("book_visible", response.get('book_name'))
        # TODO: More test cases without hard coding

    def test_get_review_by_id(self):
        print("test_get_review_by_id")
        response = c.post('/api/login/', {'e_mail': 't@t.com', 'password': 'pwd'})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        session_key = response.get('session_key')
        self.assertEqual(True, len(session_key) > 1)
        print("get review info")
        # response = c.post('/api/getReviewByID/', {'session_key': session_key, 'id': 101})
        # response = response.json()
        # self.assertEqual("verygood", response.get('review_content'))

    def test_rating_display(self):
        print("test_rating_display#1 success case")
        response = c.post('/api/login/', {'e_mail': 't@t.com', 'password': 'pwd'})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        session_key = response.get('session_key')
        self.assertEqual(True, len(session_key) > 1)
        response = c.post('/api/rating_display/', {'session_key': session_key, 'id': 100})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        print("test_rating_display#2 wrong session key")
        response = c.post('/api/rating_display/', {'session_key': 'dfasfsadfasfsadfsaf', 'id': 100})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual('session expired', response.get('reason'))
        print("test_rating_display#3 no session key")
        response = c.post('/api/rating_display/', {'id': 100})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual('no session key', response.get('reason'))
        print("test_rating_display#4 no ISBN key")
        response = c.post('/api/rating_display/', {'session_key': session_key})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual('no bookid key', response.get('reason'))

    def test_comments_display(self):
        print("test_comments_display#1 success case")
        response = c.post('/api/login/', {'e_mail': 't@t.com', 'password': 'pwd'})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        session_key = response.get('session_key')
        self.assertEqual(True, len(session_key) > 1)
        response = c.post('/api/comments_display/', {'session_key': session_key, 'id': 1001})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        print("test_comments_display#2 wrong session key")
        response = c.post('/api/comments_display/', {'session_key': 'dfasfsadfasfsadfsaf', 'id': 1001})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual('session expired', response.get('reason'))
        print("test_comments_display#3 no session key")
        response = c.post('/api/comments_display/', {'id': 1001})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual('no session key', response.get('reason'))
        print("test_comments_display#4 no review")
        response = c.post('/api/comments_display/', {'session_key': session_key})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual('no reviewid', response.get('reason'))

    def test_vote_display(self):
        print("test_vote_display#1 success case")
        response = c.post('/api/login/', {'e_mail': 't@t.com', 'password': 'pwd'})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        session_key = response.get('session_key')
        self.assertEqual(True, len(session_key) > 1)
        response = c.post('/api/vote_display/', {'session_key': session_key, 'id': 1001})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        print("test_vote_display#2 wrong session key")
        response = c.post('/api/vote_display/', {'session_key': 'dfasfsadfasfsadfsaf', 'id': 1001})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual('session expired', response.get('reason'))
        print("test_vote_display#3 no session key")
        response = c.post('/api/vote_display/', {'id': 1001})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual('no session key', response.get('reason'))
        print("test_vote_display#4 no review")
        response = c.post('/api/vote_display/', {'session_key': session_key})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual('no reviewid', response.get('reason'))

    def test_edit_comment(self):
        print("test_edit_comment#1 success case")
        response = c.post('/api/login/', {'e_mail': 'michael@example.com', 'password': 'Password123'})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        session_key = response.get('session_key')
        self.assertEqual(True, len(session_key) > 1)
        response = c.post('/api/edit_comment/', {'session_key': session_key, 'id': 10011, 'content': 'miaomiaomiao'})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        print("test_edit_comment#2 wrong session key")
        response = c.post('/api/edit_comment/',
                          {'session_key': 'dfasfsadfasfsadfsaf', 'id': 10011, 'content': 'miaomiaomiao'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual('session expired', response.get('reason'))
        print("test_edit_comment#3 no session key")
        response = c.post('/api/edit_comment/', {'id': 10011, 'content': 'miaomiaomiao'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual('no session key', response.get('reason'))
        print("test_edit_comment#4 no comment")
        response = c.post('/api/edit_comment/', {'session_key': session_key, 'content': 'miaomiaomiao'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual('no commentid', response.get('reason'))
        print("test_edit_comment#4 illegal user")
        response = c.post('/api/login/', {'e_mail': 't@t.com', 'password': 'pwd'})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        session_key = response.get('session_key')
        self.assertEqual(True, len(session_key) > 1)
        response = c.post('/api/edit_comment/', {'session_key': session_key, 'id': 10011, 'content': 'miaomiaomiao'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual('illegal user', response.get('reason'))

    def test_delete_review(self):
        print("test_delete_review success")
        response = c.post('/api/login/', {'e_mail': 'michael@example.com', 'password': 'Password123'})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        session_key = response.get('session_key')
        self.assertEqual(True, len(session_key) > 1)
        response = c.post('/api/deleteReviewByID/', {'session_key': session_key, 'id': 999})
        response = response.json()
        self.assertEqual("Normal user", response.get('permission'))
        self.assertEqual("success", response.get('status'))

    def test_setPassword(self):
        print("test set password #1: successful case")
        response = c.post('/api/login/', {'e_mail': 'michael@example.com', 'password': 'Password123'})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        session_key = response.get('session_key')
        self.assertEqual(True, len(session_key) > 1)
        response = c.post('/api/setPassword/', {'session_key': session_key, 'NewPassword': 'Password1234',
                                                'OldPassword': 'Password123', 'NewPassword2': 'Password1234'})
        print(response)
        response = response.json()
        self.assertEqual("success", response.get('status'))

        print("test set password #2: no new password")
        response = c.post('/api/setPassword/',
                          {'session_key': session_key, 'OldPassword': 'Pasword1234', 'NewPassword2': ''})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual("missing password", response.get('reason'))

        print("test set password $3: password doesn't match")
        response = c.post('/api/setPassword/', {'session_key': session_key, 'NewPassword': 'Password12345',
                                                'OldPassword': 'Pasword1234', 'NewPassword2': 'Password123456'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual("passwords do not match", response.get('reason'))

        print("test set password #4: authentication failed")
        response = c.post('/api/setPassword/', {'session_key': session_key, 'NewPassword': 'Password1234',
                                                'OldPassword': 'Password1', 'NewPassword2': 'Password1234'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual("authentication failure", response.get('reason'))

    def test_setName(self):
        print("test set name #1: successful case")
        response = c.post('/api/login/', {'e_mail': 'michael@example.com', 'password': 'Password123'})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        session_key = response.get('session_key')
        self.assertEqual(True, len(session_key) > 1)
        response = c.post('/api/setName/', {'session_key': session_key, 'NewName': 'Mike',
                                            'Password': 'Password123'})
        response = response.json()
        self.assertEqual("success", response.get('status'))

        print("test set name #2: missing password")
        response = c.post('/api/setName/', {'session_key': session_key, 'NewName': 'Mike'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual("password required", response.get('reason'))

        print("test set name #3: missing new name")
        response = c.post('/api/setName/', {'session_key': session_key, 'Password': 'Password123'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual("update data missing", response.get('reason'))

        print("test set name #4: authentication failed")
        response = c.post('/api/setName/', {'session_key': session_key, 'NewName': 'John',
                                            'Password': 'Password1'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual("authentication failure", response.get('reason'))

        print("test set name #5: set to an existing name")
        response = c.post('/api/setName/', {'session_key': session_key, 'NewName': 'Mike',
                                            'Password': 'Password123'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual("existing_username", response.get('reason'))

    def test_setGender(self):
        print("test set gender #1: successful case")
        response = c.post('/api/login/', {'e_mail': 'michael@example.com', 'password': 'Password123'})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        session_key = response.get('session_key')
        self.assertEqual(True, len(session_key) > 1)
        response = c.post('/api/setGender/', {'session_key': session_key, 'NewGender': 'Female',
                                              'Password': 'Password123'})
        response = response.json()
        self.assertEqual("success", response.get('status'))

        print("test set gender #2: missing input")
        response = c.post('/api/setGender/', {'session_key': session_key, 'Password': 'Password123'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual("update data missing", response.get('reason'))

        print("test set gender #3: invalid input")
        response = c.post('/api/setGender/', {'session_key': session_key, 'NewGender': 'Test',
                                              'Password': 'Password123'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual("invalid input", response.get('reason'))

        print("test set gender #4: no password")
        response = c.post('/api/setGender/', {'session_key': session_key, 'NewGender': 'Female'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual("password required", response.get('reason'))

        print("test set gender #5: authentication failed")
        response = c.post('/api/setGender/', {'session_key': session_key, 'NewGender': 'Female',
                                              'Password': 'Password1'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual("authentication failed", response.get('reason'))

    def test_setEmail(self):
        print("test set email #1: successful case")
        response = c.post('/api/login/', {'e_mail': 'michael@example.com', 'password': 'Password123'})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        session_key = response.get('session_key')
        self.assertEqual(True, len(session_key) > 1)
        response = c.post('/api/setEmail/', {'session_key': session_key, 'NewEmail': 'mike@example.com',
                                             'Password': 'Password123'})
        response = response.json()
        self.assertEqual("success", response.get('status'))

        print("test set email #2: missing email")
        response = c.post('/api/setEmail/', {'session_key': session_key, 'Password': 'Password123'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual("update data missing", response.get('reason'))

        print("test set email #3: missing password")
        response = c.post('/api/setEmail/', {'session_key': session_key, 'NewEmail': 'mike@example.com'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual("password required", response.get('reason'))

        print("test set email #4: authentication failed")
        response = c.post('/api/setEmail/', {'session_key': session_key, 'NewEmail': 'qqqqqq@example.com',
                                             'Password': 'Password1'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual("authentication failed", response.get('reason'))

    def test_setIntro(self):
        print("test set intro #1: successful case")
        response = c.post('/api/login/', {'e_mail': 'michael@example.com', 'password': 'Password123'})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        session_key = response.get('session_key')
        self.assertEqual(True, len(session_key) > 1)
        response = c.post('/api/setIntro/', {'session_key': session_key, 'NewIntro': 'Cogito ergo sum',
                                             'Password': 'Password123'})
        response = response.json()
        self.assertEqual("success", response.get('status'))

        print("test set intro #2: missing input")
        response = c.post('/api/setIntro/', {'session_key': session_key, 'Password': 'Password123'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual("update data missing", response.get('reason'))

        print("test set intro #3: missing password")
        response = c.post('/api/setIntro/', {'session_key': session_key, 'NewIntro': 'Cogito ergo sum'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual("password required", response.get('reason'))

        print("test set intro #4: authentication failed")
        response = c.post('/api/setIntro/', {'session_key': session_key, 'NewIntro': 'Cogito ergo sum',
                                             'Password': 'Password1'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual("authentication failed", response.get('reason'))
    
    def test_add_comment(self):
        print("test_add_comment#1 success case")
        response = c.post('/api/login/', {'e_mail': 'michael@example.com', 'password': 'Password123'})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        session_key = response.get('session_key')
        self.assertEqual(True, len(session_key) > 1)
        response = c.post('/api/addComment/', {'session_key': session_key, 'id': 999, 'content': 'some random comments'})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        print("test_add_comment#2 wrong session key")
        response = c.post('/api/addComment/',
                          {'session_key': 'dfasfsadfasfsadfsaf', 'id': 999, 'content': 'miaomiaomiao'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual('session expired', response.get('reason'))
        print("test_add_comment#3 missing content")
        response = c.post('/api/addComment/', {'session_key': session_key, 'id': 999, 'content': ''})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        print("test_add_comment#4 non-existing review")
        response = c.post('/api/addComment/',
                          {'session_key': session_key, 'id': 428932, 'content': 'miaomiaomiao'})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual('Review does not exist', response.get('reason'))

    def test_get_books_by_isbn(self):
        print("test get book by ISBN case #1: success")
        response = c.post('/api/login/', {'e_mail': 't@t.com', 'password': 'pwd'})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        session_key = response.get('session_key')
        self.assertEqual(True, len(session_key) > 1)
        response = c.post('/api/get_books_by_isbn', {'session_key': session_key, 'isbn': '123456789-1'})
        response = response.json()
        self.assertEqual("success", response.get('status'))

        print("test get nook by ISBN case #2: missing ISBN code")
        response = c.post('/api/get_books_by_isbn', {'session_key': session_key})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual("no ISBN", response.get('reason'))

    def test_get_books_by_author(self):
        print("test get book by author case #1: success")
        response = c.post('/api/login/', {'e_mail': 't@t.com', 'password': 'pwd'})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        session_key = response.get('session_key')
        self.assertEqual(True, len(session_key) > 1)
        response = c.post('/api/get_books_by_author', {'session_key': session_key, 'author': 'test_author'})
        response = response.json()
        self.assertEqual("success", response.get('status'))

        print("test get book by author case #2: missing author name")
        response = c.post('/api/get_books_by_author', {'session_key': session_key})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual("no author", response.get('reason'))

    def test_get_book_by_publish_firm(self):
        print("test get book by author case #1: success")
        response = c.post('/api/login/', {'e_mail': 't@t.com', 'password': 'pwd'})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        session_key = response.get('session_key')
        self.assertEqual(True, len(session_key) > 1)
        response = c.post('/api/get_books_by_publish_firm',
                          {'session_key': session_key, 'publish_firm': 'test_firm'})
        response = response.json()
        self.assertEqual("success", response.get('status'))
        print("test get book by author case #2: missing author name")
        response = c.post('/api/get_books_by_publish_firm', {'session_key': session_key})
        response = response.json()
        self.assertEqual("fail", response.get('status'))
        self.assertEqual("no publish firm", response.get('reason'))


class UtilsTestCase(TestCase):
    def setUp(self):
        permission_m = 'moderator'
        permission_b = 'banned'
        User.objects.create(e_mail='t@t.com', password=make_password('pwd'))
        moderator = User.objects.create(e_mail='m@m.com', password=make_password('pwd'))
        moderator.permission = permission_m
        banned_user = User.objects.create(e_mail='b@b.com', password=make_password('pwd'))
        banned_user.permission = permission_b
        banned_user.save()
        moderator.save()

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

    def test_get_user_permission_type(self):
        print("test_get_user_permission_type")
        self.assertEqual('Normal user', get_user_permission_type(User.objects.get(e_mail='t@t.com')))
        self.assertEqual('Banned user', get_user_permission_type(User.objects.get(e_mail='b@b.com')))
        self.assertEqual('Moderator', get_user_permission_type(User.objects.get(e_mail='m@m.com')))
