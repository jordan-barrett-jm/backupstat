from django import forms


class UserForm(forms.Form):
   username = forms.CharField(label="Username", max_length=100)
   email = forms.CharField(label="Email Address", max_length=100, required=False)
   password = forms.CharField(label="Password", widget=forms.PasswordInput())
