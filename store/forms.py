from django import forms

class aggiungiProdottoForm(forms.Form):
    nome = forms.CharField(label='Nome', max_length=100)
    descrizione = forms.CharField(label='Descrizione', max_length=300)
    prezzo = forms.FloatField()
    categoria = forms.CharField(label='Categoria', max_length=30)
    visibile = forms.BooleanField(required=False)

class modificaProdottoForm(forms.Form):
    nome = forms.CharField(label='Nome', max_length=100, required=False)
    descrizione = forms.CharField(label='Descrizione', max_length=300, required=False)
    prezzo = forms.FloatField(required=False)
    categoria = forms.CharField(label='Categoria', max_length=30, required=False)
    visibile = forms.BooleanField(required=False)

class cercaProdottoForm(forms.Form):
    ricerca =forms.CharField(max_length=100)