from django.test import TestCase
from django.contrib.auth.models import User
from accounts.models import User_Request

from accounts.tests.common.mixins import TestDataMixin

class UserProfileTest(TestDataMixin, TestCase):

    def test_create_profile_success(self):
        profile = User.objects.create_user(username="tester", password="postgrse").profile
        self.assertTrue(profile)

class UserRequestTest(TestDataMixin, TestCase):

    def setUp(self):
        self.second_user = User.objects.get(username="pol")
        self.organization = self.second_user.profile.organization

    def test_create_friend_request_success(self):
        friend_request = User_Request.objects.create(from_user = self.user, to_user = self.second_user, type_request= "friend")
        self.assertTrue(friend_request)

    def test_create_manager_request_success(self):
        manager_request = User_Request.objects.create(from_user = self.user, to_user = self.second_user, type_request= "manager")
        self.assertTrue(manager_request)

    def test_create_join_organization_request_success(self):
        join_organization_request = User_Request.objects.create(from_user = self.user, to_user = self.second_user, organization=self.organization, type_request= "join organization")
        self.assertTrue(join_organization_request)

