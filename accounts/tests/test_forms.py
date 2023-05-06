from django.test import TestCase

from accounts.forms import ImageChangeForm, ProfileForm, SignupForm, User_Email_Form


class SignupFormTest(TestCase):

    def test_signup_success(self):
        valid_data = {
            'username' : 'test',
            'email' : 'test@gmail.com',
            'password1' : 'postgrse',
            'password2' : 'postgrse',
        }
        form = SignupForm(data=valid_data)
        form.is_valid()

        self.assertFalse(form.errors)

    def test_signup_failed(self):
        invalid_data = {
            'username' : 'test',
            'email' : 'test@gmail.com',
            'password1' : 'sda',
            'password2' : 'test123',
        }
        form = SignupForm(data=invalid_data)
        form.is_valid()

        self.assertTrue(form.errors)

class ProfileTest(TestCase):

    def test_profile_success(self):
        valid_data = {
            'first_name' : 'Daniel',
            'last_name' : 'Shafir',
            'country' : 'IL',
        }
        form = ProfileForm(data=valid_data)
        form.is_valid()

        self.assertFalse(form.errors)

    def test_profile_failed(self):
        invalid_data = {
            'first_name' : 'Daniel',
            'last_name' : 'Shafir',
            'country' : '',
        }
        form = ProfileForm(data=invalid_data)
        form.is_valid()

        self.assertTrue(form.errors)
    
    def test_profile_image_success(self):
        valid_data = {
            'image' : 'https://st3.depositphotos.com/3581215/18899/v/600/depositphotos_188994514-stock-illustration-vector-illustration-male-silhouette-profile.jpg',
        }
        form = ImageChangeForm(data=valid_data)
        form.is_valid()

        self.assertFalse(form.errors)

    def test_profile_image_fail(self):
        valid_data = {
            'image' : '',
        }
        form = ImageChangeForm(data=valid_data)
        form.is_valid()

        self.assertTrue(form.errors)

    def test_profile_email_success(self):
        valid_data = {
            'email' : 'd@gmail.com',
        }
        form = User_Email_Form(data=valid_data)
        form.is_valid()

        self.assertFalse(form.errors)

    def test_profile_email_fail(self):
        invalid_data = {
            'email' : 'test',
        }
        form = User_Email_Form(data=invalid_data)
        form.is_valid()
        
        self.assertTrue(form.errors)