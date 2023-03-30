from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Member, SavingsGroup

class MemberRegistrationForm(UserCreationForm):
    mobile_number = forms.CharField(max_length=20)
    id_number = forms.CharField(max_length=20)
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ('username', 'mobile_number', 'id_number', 'email', 'password1', 'password2')
    def save(self, commit=True):
        user = super(MemberRegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.mobile_number = self.cleaned_data['mobile_number']
        user.id_number = self.cleaned_data['id_number']
        password = self.cleaned_data.get('password1')
        user.set_password(password)
        if commit:
            user.save()
        return user

class MemberLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class DeactivateUserForm(forms.Form):
    confirm = forms.BooleanField(required=True)

class MyUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Enter a valid email address')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already in use. Please use a different email.')
        return email

class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(label="Password",
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

class SavingsGroupForm(forms.ModelForm):
    class Meta:
        model = SavingsGroup
        fields = ('name', 'description')
        



# class SavingsGroupForm(forms.ModelForm):
#     class Meta:
#         model = SavingsGroup
#         fields = ('name', 'description', 'start_date', 'end_date')
#         widgets = {
#             'start_date': forms.DateInput(attrs={'type': 'date'}),
#             'end_date': forms.DateInput(attrs={'type': 'date'}),
#         }