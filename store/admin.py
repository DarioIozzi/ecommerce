from django.contrib import admin
from .models import prodotto, carrello , ordine, ordineProdotto

# Register your models here.
admin.site.register(prodotto)
admin.site.register(carrello)
admin.site.register(ordine)
admin.site.register(ordineProdotto)