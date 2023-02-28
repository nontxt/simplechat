from ..models import Thread, Message
from .base_test import BaseTestCase


class ThreadModelTestCase(BaseTestCase):

    def test_create_thread(self):
        """
        Test creating a thread
        """
        thread = Thread.objects.create()
        self.assertEqual(thread.id, 2)
        self.assertEqual(thread.participants.count(), 0)

    def test_set_participants(self):
        """
        Test setting participants
        """
        self.assertEqual(self.thread.participants.count(), 0)
        self.thread.participants.set([self.user_1, self.user_2])
        self.assertEqual(self.thread.participants.count(), 2)
        self.assertEqual(self.thread.participants.get(id=1), self.user_1)
        self.assertEqual(self.thread.participants.get(id=2), self.user_2)

    def test_delete_thread(self):
        """
        Test deleting thread
        """
        self.assertEqual(self.thread.id, 1)
        self.thread.delete()
        with self.assertRaises(Thread.DoesNotExist):
            Thread.objects.get(id=1)

    def test_update_thread(self):
        """
        Test updating thread
        """
        update = self.thread.updated
        self.thread.update()
        self.assertNotEqual(update, self.thread.updated)


class MessageModelTestCase(BaseTestCase):
    def setUp(self):
        super(MessageModelTestCase, self).setUp()
        self.thread.participants.set([self.user_1, self.user_2])
        self.message = Message.objects.create(thread=self.thread, sender=self.user_1, text=self.fake.text())

    def test_create_message(self):
        """
        Test creating a message
        """
        text = self.fake.text()
        message = Message.objects.create(thread=self.thread, sender=self.user_2, text=text)
        self.assertEqual(message.id, 2)
        self.assertEqual(message.sender, self.user_2)
        self.assertEqual(message.text, text)
        self.assertEqual(message.thread, self.thread)
        self.assertFalse(message.is_read)

    def test_mark_as_read(self):
        """
        Test marking a message as read
        """
        self.assertFalse(self.message.is_read)
        self.message.mark_as_read()
        self.assertTrue(self.message.is_read)

    def test_delete_message(self):
        """
        Test deleting a message
        """
        self.assertEqual(self.message.id, 1)
        self.message.delete()
        with self.assertRaises(Message.DoesNotExist):
            Message.objects.get(id=1)

    def test_delete_cascade_by_user(self):
        """
        Test deleting message by cascade when user was deleted
        """
        self.assertEqual(self.message.id, 1)
        self.user_1.delete()
        with self.assertRaises(Message.DoesNotExist):
            Message.objects.get(id=1)

    def test_delete_cascade_by_thread(self):
        """
        Test deleting message by cascade when thread was deleted
        """
        self.assertEqual(self.message.id, 1)
        self.thread.delete()
        with self.assertRaises(Message.DoesNotExist):
            Message.objects.get(id=1)
