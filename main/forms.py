from django import forms
from .models import RequestQueue


class NewRequest(forms.ModelForm):
    class Meta:
        model = RequestQueue
        fields = ('request',)
