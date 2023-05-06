from urllib import response
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from accounts.tests.common.mixins import TestDataMixin

class LoginTest(TestDataMixin, TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.user.email = "Test@g.com"
        cls.user.save()
        cls.profile = cls.user.profile
        cls.profile.first_name = 'Test'
        cls.profile.last_name = 'Subject'
        cls.profile.country = "IL"
        cls.profile.save()
    
    def test_login_success(self):
        response = self.client.get(reverse('login'))
        login_user = self.client.login(**self.credentials)
        after_login = self.client.post(reverse('login'), **self.credentials)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(login_user)
    
    def test_login_fail(self):
        response = self.client.get(reverse('login'))
        login_user = self.client.login(username='pol', password='none')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(login_user)

    def test_login_success_redirect(self):
        login = self.client.post(reverse('login'), **self.credentials)
        self.client.get(reverse('login'))
        self.client.login(**self.credentials)
        homepage = self.client.request()
        self.assertEqual(login.status_code, 200)
        self.assertContains(homepage, "Hello")

    def test_logout(self):
        self.client.login(**self.credentials)
        result = self.client.logout()
        self.assertEqual(result, None)

    def test_edit_profile(self):
        self.client.login(**self.credentials)
        response = self.client.get(reverse('profile_edit'))
        self.assertEqual(response.status_code, 200)
    
    def test_edit_email(self):
        self.client.login(**self.credentials)
        self.user.email = ''
        self.user.save()
        response = self.client.get(reverse('profile_edit_email'))
        self.assertEqual(response.status_code, 200)
    
    def test_edit_image(self):
        self.client.login(**self.credentials)
        response = self.client.get(reverse('update-image'))
        self.assertEqual(response.status_code, 200)
