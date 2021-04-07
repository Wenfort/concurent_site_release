from django import forms
from .models import RequestQueue, Ticket, TicketPost
from django.contrib.auth.models import User


class NewRequest(forms.ModelForm):
    class Meta:
        model = RequestQueue
        fields = ('request_id',)


class NewUser(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'password', 'email',)


class AuthUser(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'password',)


class NewTicketPost(forms.ModelForm):
    class Meta:
        model = TicketPost
        fields = ('ticket_post_text',)


class ChangePassword(forms.ModelForm):
    class Meta:
        model = User
        fields = ('password',)