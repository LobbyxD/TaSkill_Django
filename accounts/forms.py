from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import UserProfile

###############
### Sign-up ###
###############

class SignupForm(UserCreationForm):

    username = forms.CharField(max_length=15)
    email = forms.CharField(max_length=100)
    password1 = forms.CharField(widget=forms.PasswordInput(), label='Password')
    password2 = forms.CharField(widget=forms.PasswordInput(), label='Confirm Password')
   
    class Meta:
        model = User
        fields = ['username','email','password1','password2']

###############
### Profile ###
###############
   
class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = '__all__'
        exclude = ['user','slug','manager', 'image','friends', 'organization']

class ImageChangeForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['image']

class User_Email_Form(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']