from django.contrib import admin
from .models import Prodotto, Carrello , Ordine, OrdineProdotto

# Register your models here.
admin.site.register(Prodotto)
admin.site.register(Carrello)
admin.site.register(Ordine)
admin.site.register(OrdineProdotto)