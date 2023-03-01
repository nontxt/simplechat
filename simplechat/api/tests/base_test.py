from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.status import HTTP_401_UNAUTHORIZED, HTTP_405_METHOD_NOT_ALLOWED
from django.contrib.auth.models import User
from ..models import Thread, Message
from faker import Faker


class BaseTestCase(TestCase):
    def setUp(self):
        self.fake = Faker()
        self.user_1 = User.objects.create_user(username=self.fake.simple_profile()['username'],
                                               email=self.fake.email(),
                                               password=self.fake.password())
        self.user_2 = User.objects.create_user(username=self.fake.simple_profile()['username'],
                                               email=self.fake.email(),
                                               password=self.fake.password())
        self.thread = Thread.objects.create()


class BaseAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.fake = Faker()
        self.user_1 = User.objects.create_user(username=self.fake.simple_profile()['username'],
                                               email=self.fake.email(),
                                               password=self.fake.password())
        self.user_2 = User.objects.create_user(username=self.fake.simple_profile()['username'],
                                               email=self.fake.email(),
                                               password=self.fake.password())
        self.stranger = User.objects.create_user(username=self.fake.simple_profile()['username'],
                                                 email=self.fake.email(),
                                                 password=self.fake.password())

        self.user_1_access_token = str(AccessToken.for_user(self.user_1))
        self.user_2_access_token = str(AccessToken.for_user(self.user_1))
        self.stranger_access_token = str(AccessToken.for_user(self.stranger))
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user_1_access_token)

        self.thread = Thread.objects.create()
        self.thread.participants.set([self.user_1, self.user_2])
        self.message = Message.objects.create(sender=self.user_1, thread=self.thread, text=self.fake.text())

    def test_unauthorised(self):
        """
        Test that unauthorised user can't use api
        """
        client = APIClient()
        # Define methods and urls
        requests = {
            client.get: [
                reverse('unread-list'),
                reverse('messages', kwargs={'username': self.user_2.username}),
                reverse('thread-list'),
                reverse('thread-detail', kwargs={'username': self.user_2.username})
            ],
            client.post: [
                reverse('unread-mark-as-read'),
                reverse('messages', kwargs={'username': self.user_2.username})
            ],
            client.delete: [
                reverse('thread-detail', kwargs={'username': self.user_2.username})
            ]
        }
        for method, urls in requests.items():
            for url in urls:
                response = method(url)
                self.assertEqual(response.status_code,
                                 HTTP_401_UNAUTHORIZED,
                                 msg=f'endpoint: {url.title().lower()}')
                self.assertDictEqual(response.json(), {'detail': 'Authentication credentials were not provided.'})

    def test_not_allowed_method(self):
        """
        Test that user can't use api with not allowed method
        """
        # Define not allowed methods and urls
        requests = {
            self.client.post: [
                reverse('thread-list'),
                reverse('thread-detail', kwargs={'username': self.user_2.username})
            ],
            self.client.put: [
                reverse('unread-mark-as-read'),
                reverse('messages', kwargs={'username': self.user_2.username}),
                reverse('thread-list'),
                reverse('thread-detail', kwargs={'username': self.user_2.username}),
            ],
            self.client.patch: [
                reverse('unread-mark-as-read'),
                reverse('messages', kwargs={'username': self.user_2.username}),
                reverse('thread-list'),
                reverse('thread-detail', kwargs={'username': self.user_2.username})
            ],
            self.client.delete: [
                reverse('unread-list'),
                reverse('messages', kwargs={'username': self.user_2.username}),
                reverse('thread-list')
            ]
        }
        for method, urls in requests.items():
            for url in urls:
                response = method(url)
                self.assertEqual(response.status_code,
                                 HTTP_405_METHOD_NOT_ALLOWED,
                                 msg=f'endpoint: {url.title().lower()}')
                self.assertDictEqual(response.json(), {'detail': f'Method "{method.__name__.upper()}" not allowed.'})
