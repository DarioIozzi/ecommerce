from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    birth_date = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}))
    is_premium = forms.BooleanField(required=False)

    class Meta:
        model = CustomUser
        fields = (
            'username',
            'first_name',   # <-- al posto di "nome"
            'last_name',    # <-- al posto di "cognome"
            'email',
            'birth_date',
            'is_premium',
            'password1',
            'password2',
        )
        labels = {
            'first_name': 'Nome',
            'last_name': 'Cognome',
            'birth_date': 'Data di nascita',
            'is_premium': 'Utente premium',
        }