from django import forms
from .models import RequestQueue
from django.contrib.auth.models import User


class NewRequest(forms.ModelForm):
    class Meta:
        model = RequestQueue
        fields = ('request',)


class NewUser(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'password', 'email',)
