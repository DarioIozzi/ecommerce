from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegistrationForm(UserCreationForm):
    username = forms.CharField(max_length=30)
    nome = forms.CharField(max_length=30)
    cognome = forms.CharField(max_length=30)
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["nome"] = self.fields.pop("nome")
        self.fields["cognome"] = self.fields.pop("cognome")
    class Meta:
        model = User
        fields = ('username', 'nome', 'cognome', 'email', 'password1', 'password2')