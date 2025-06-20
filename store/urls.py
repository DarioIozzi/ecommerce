from django.urls import path , include
from . import views

urlpatterns = [
    path("", views.home),

    path("home/", views.home, name="home"),

    path("cliente/", views.cliente, name="cliente"),

    path("aggiungiProdotto/", views.aggiungiProdotto, name="aggiungiProdotto"),

    path("gestioneProdotti/", views.gestioneProdotti, name="gestioneProdotti"),

    path("gestioneAcquisto/", views.gestioneAcquisto, name="gestioneAcquisto"),

    path("aggiungiAlCarrello/", views.aggiungiAlCarrello, name="aggiungiAlCarrello"),

    path("effettuaOrdine/", views.effettuaOrdine, name="effettuaOrdine"),

    path("revisioneOrdine/", views.revisioneOrdine, name="revisioneOrdine"),

    path("gestioneCarrello/", views.gestioneCarrello, name="gestioneCarrello"),

    path("salvaPagamento/", views.salvaPagamento, name="salvaPagamento"),

    path("vediOrdine/", views.vediOrdine, name="vediOrdine"),

    path("cronologiaOrdini/", views.cronologiaOrdini, name="cronologiaOrdini"),

    path('carrello/',views.gestioneCarrello, name='viewCarrello'),
]