from django.contrib.auth.forms import AuthenticationForm
from django import forms
from .models import Account

class LoginForm(AuthenticationForm):
    pass

class AccountProxyForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['proxyip', 'proxyport', 'proxyuser', 'proxypass']
