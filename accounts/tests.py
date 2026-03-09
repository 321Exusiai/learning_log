from django.test import TestCase
from django.contrib.auth.models import User


class UserTestCase(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(username='test', password='123456')
        self.assertEqual(user.username, 'test')

    def test_create_superuser(self):
        user = User.objects.create_superuser(username='admin', password='admin123')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_user_str(self):
        user = User.objects.create_user(username='testuser', password='password123')
        self.assertEqual(str(user), 'testuser')
