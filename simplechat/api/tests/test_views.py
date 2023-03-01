from rest_framework import status
from django.urls import reverse
from ..models import Thread, Message
from .base_test import BaseAPITestCase


class ThreadAPIViewTestCase(BaseAPITestCase):

    def test_create_thread(self):
        """
        Test that a user can create a thread
        """
        url = reverse('thread-detail', kwargs={'username': self.stranger.username})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['interlocutor'], self.stranger.username)

    def test_create_thread_with_not_existed_user(self):
        """
        Test that a user can't create a thread with not existed user
        """
        url = reverse('thread-detail', kwargs={'username': 'not_existed_user'})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_thread_with_themself_user(self):
        """
        Test that a user can't create a thread with himself
        """
        url = reverse('thread-detail', kwargs={'username': self.user_1.username})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_thread(self):
        """
        Test that a user can get an existed thread
        """
        Message.objects.create(sender=self.user_2, thread=self.thread, text=self.fake.text())
        url = reverse('thread-detail', kwargs={'username': self.user_2.username})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['interlocutor'], self.user_2.username)
        self.assertIs(type(response.json()['messages']), list)
        self.assertEqual(len(response.json()['messages']), 2)

    def test_delete_thread(self):
        """
        Test that a user can delete an existed thread
        """
        url = reverse('thread-detail', kwargs={'username': self.user_2.username})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Thread.objects.count(), 0)

    def test_delete_not_existed_thread(self):
        """
        Test that a user can't delete a not existed thread
        """
        url = reverse('thread-detail', kwargs={'username': 'not_existed_user'})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_threads(self):
        """
        Test that a user can list his threads.
        Thread must contain the last message if it exists
        """

        Message.objects.create(sender=self.user_1, thread=self.thread, text=self.fake.text())
        thread = Thread.objects.create()
        thread.participants.set([self.user_1, self.stranger])

        url = reverse('thread-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], 2)

        results = response.json()['results']
        self.assertEqual(results[0]['messages'], [])
        self.assertEqual(results[0]['interlocutor'], self.stranger.username)

        self.assertEqual(results[1]['messages']['id'], 2)
        self.assertEqual(results[1]['interlocutor'], self.user_2.username)

    def test_cant_list_strangers_threads(self):
        """
        Test that a user can't list strangers threads.
        """
        # Create a new thread between user_2 and stranger without messages
        thread = Thread.objects.create()
        thread.participants.set([self.user_2, self.stranger])

        url = reverse('thread-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], 1)

        results = response.json()['results'][0]
        self.assertEqual(results['interlocutor'], self.user_2.username)
        self.assertNotEqual(results['messages'], [])


class MessageAPIViewTestCase(BaseAPITestCase):

    def test_get_messages(self):
        """
        Test that a user can get messages for thread
        """
        Message.objects.create(sender=self.user_2, thread=self.thread, text=self.fake.text())
        url = reverse('messages', kwargs={'username': self.user_2.username})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], 2)

        results = response.json()['results'][0]
        self.assertEqual(results['id'], 2)
        self.assertEqual(results['sender_name'], self.user_2.username)
        self.assertFalse(results['is_read'])

    def test_get_messages_for_not_existed_thread(self):
        """
        Test that a user can't get messages for not existed thread
        """
        url = reverse('messages', kwargs={'username': self.stranger.username})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_message(self):
        """
        Test that a user can create a message
        """
        text = self.fake.text()
        url = reverse('messages', kwargs={'username': self.user_2.username})
        response = self.client.post(url, data={'text': text})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(data['id'], 2)
        self.assertEqual(data['sender_name'], self.user_1.username)
        self.assertFalse(data['is_read'])
        self.assertEqual(data['text'], text)

    def test_create_message_for_not_existed_thread(self):
        """
        Test that a user can't create a message for not existed thread
        """
        url = reverse('messages', kwargs={'username': self.stranger.username})
        response = self.client.post(url, data={'text': self.fake.text()})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_do_not_get_own_unread_messages(self):
        """
        Test that a user can't get own unread messages
        """
        self.assertEqual(self.thread.messages.count(), 1)
        self.assertFalse(self.message.is_read)

        url = reverse('unread-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], 0)
        self.assertEqual(response.json()['results'], [])

    def test_get_unread_messages(self):
        """
        Test that a user can get unread messages
        """
        self.assertEqual(self.thread.messages.count(), 1)
        # Add 6 new messages
        for _ in range(5):
            Message.objects.create(sender=self.user_2, thread=self.thread, text=self.fake.text())
        else:
            last_message = Message.objects.create(sender=self.user_2, thread=self.thread, text=self.fake.text())
            # Mark last message as read
            last_message.mark_as_read()
            self.assertEqual(last_message.id, 7)

        self.assertEqual(self.thread.messages.count(), 7)

        url = reverse('unread-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.json()['count'], 5)

        results = response.json()['results']
        self.assertEqual(results[0]['id'], 6)
        self.assertEqual(results[-1]['id'], 5)

    def test_mark_as_read_single_message(self):
        """
        Test that a user can mark a single message as read
        """

        message = Message.objects.create(sender=self.user_2, thread=self.thread, text=self.fake.text())
        self.assertFalse(message.is_read)

        url = reverse('unread-mark-as-read')
        response = self.client.post(url, data={"message_id": 2})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        message = Message.objects.get(id=2)
        self.assertTrue(message.is_read)

    def test_mark_as_read_multiple_messages(self):
        """
        Test that a user can mark multiple messages as read
        """
        for _ in range(5):
            Message.objects.create(sender=self.user_2, thread=self.thread, text=self.fake.text())

        url = reverse('unread-mark-as-read')
        response = self.client.post(url, data={"message_id": [2, 3, 4, 5, 6]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        unread_messages = Message.objects.filter(thread=self.thread, is_read=False)
        self.assertEqual(unread_messages.count(), 1)
        message = unread_messages.first()
        self.assertFalse(message.is_read)
        self.assertEqual(message.id, self.message.id)

    def test_mark_as_read_without_required_parameter(self):
        """
        Test that a user get HTTP_400_BAD_REQUEST if missed required parameter
        """
        url = reverse('unread-mark-as-read')
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_mark_as_read_not_existed_message(self):
        """
        Test that a user get NotFound if tried mark not existed message
        """
        url = reverse('unread-mark-as-read')
        response = self.client.post(url, data={"message_id": 99})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.post(url, data={"message_id": [99, 98, 97]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_do_not_mark_as_read_own_message(self):
        """
        Test that a user can't mark own message as read
        """

        self.assertEqual(self.message.sender, self.user_1)
        self.assertEqual(self.message.id, 1)

        url = reverse('unread-mark-as-read')
        response = self.client.post(url, data={"message_id": 1})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        message = Message.objects.get(id=1)
        self.assertFalse(message.is_read)
        self.assertEqual(message.id, self.message.id)
