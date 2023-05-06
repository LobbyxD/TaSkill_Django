from django.test import TestCase
from django.contrib.auth.models import User,Group

class TestDataMixin(TestCase):

    fixtures = [
        'groups.json',
        'users.json',
        'profiles.json',
        # 'tasks.json',
        'task_statuses.json',
        'task_status_links.json',
        # 'boards.json',
        # 'board_permissions.json',
        'organizations.json',
        'organization_permissions.json',
        ]

    @classmethod
    def setUpTestData(cls) -> None:
        cls.group = Group.objects.get_or_create(name="guest")
        cls.superuser = User.objects.get(username="lobbyx3")
        cls.user = User.objects.get(username='pol')
        cls.profile = cls.user.profile
        cls.organization = cls.profile.organization
