from django.db import models
from django.conf import settings

# Create your models here.

class Prodotto(models.Model):
    nome = models.CharField(max_length=100)
    descrizione = models.CharField(max_length=300)
    prezzo = models.FloatField()
    categoria = models.CharField(max_length=30, default="None")
    visibile = models.BooleanField(default=True)

    def __str__(self):
        return self.nome + " | " + self.descrizione + " , prezzo: " + str(self.prezzo) + "€"

class Ordine(models.Model):
    cliente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    data = models.DateTimeField(auto_now_add=True)
    carta = models.CharField(max_length=16, default="0000000000000000")
    cvv = models.CharField(max_length=3, default="000")

    def __str__(self):
        data = self.data.strftime("%d/%m/%Y %H:%M")
        return "ordine effettuato da "+self.cliente.username+" - "+str(data)

class OrdineProdotto(models.Model):
    prodotto = models.ForeignKey(Prodotto, on_delete=models.CASCADE)
    ordine = models.ForeignKey(Ordine, on_delete=models.CASCADE)
    quantita = models.IntegerField()

    def __str__(self):
        return str(self.prodotto)+", quantità: "+str(self.quantita)

class Carrello(models.Model):
    prodotto = models.ForeignKey(Prodotto, on_delete=models.CASCADE)
    cliente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quantita = models.IntegerField()

    def __str__(self):
        return "carrello di "+ str(self.cliente)+": "+str(self.prodotto)+", quantità: "+str(self.quantita)