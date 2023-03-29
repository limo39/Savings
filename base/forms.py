from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Member

class MemberRegistrationForm(UserCreationForm):
    mobile_number = forms.CharField(max_length=20)
    id_number = forms.CharField(max_length=20)
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ('username', 'mobile_number', 'id_number', 'email', 'password1', 'password2')

class MemberLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class DeactivateUserForm(forms.Form):
    confirm = forms.BooleanField(required=True)
