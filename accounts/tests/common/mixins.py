from django.test import TestCase
from django.contrib.auth.models import User,Group

class TestDataMixin(TestCase):

    fixtures = ['groups.json', 'users.json']

    @classmethod
    def setUpTestData(cls) -> None:
        cls.group = Group.objects.get_or_create(name="guest")
        cls.user = User.objects.create_user(username='test', password='postgrse')
        cls.profile = cls.user.profile
        cls.credentials = {"username": "test", "password": "postgrse"}

