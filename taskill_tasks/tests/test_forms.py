from django.test import TestCase

from taskill_tasks.forms import Board_Creation, Give_Organization_Permission, Organization_Creation
from taskill_tasks.models import Task_status_link
from taskill_tasks.tests.common.mixins import TestDataMixin


class FormsTest(TestDataMixin,TestCase):

    def test_organization_create_success(self):
        valid_data = {
            'name' : 'Organization',
        }
        form = Organization_Creation(data=valid_data, user = self.user)
        form.is_valid()

        self.assertFalse(form.errors)
    
    def test_organization_create_fail(self):
        invalid_data = {
            'name' : '',
        }
        form = Organization_Creation(data=invalid_data, user = self.user)
        form.is_valid()

        self.assertTrue(form.errors)
    
    def test_give_permission_success(self):
        valid_data = {
            'organization': self.organization,
            'user': self.organization.profiles.first().user.id,
            'permissions' : 'boards_view'
        }
        form = Give_Organization_Permission(data=valid_data, user= self.user, organization= self.organization)
        form.is_valid()
        self.assertFalse(form.errors)
    
    def test_give_permission_fail(self):
        invalid_data = {
            'organization': self.organization,
            'user' : None,
            'permissions' : 'owner'
        }
        form = Give_Organization_Permission(data= invalid_data, user= self.user, organization= self.organization)
        form.is_valid()

        self.assertTrue(form.errors)

    def test_board_create_success(self):
        valid_data = {
            "organization": self.organization,
            "name": 'self.organization',
            "initial_task_status": Task_status_link.objects.first(),
        }
        form = Board_Creation(data=valid_data, user = self.user)
        form.is_valid()

        self.assertFalse(form.errors)
    
    def test_board_create_fail(self):
        invalid_data = {
            "organization": self.organization,
            "name": '',
            "initial_task_status": Task_status_link.objects.first(),
        }
        form = Board_Creation(data=invalid_data, user = self.user)
        form.is_valid()

        self.assertTrue(form.errors)
    
