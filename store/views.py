from django.shortcuts import render
from django.http import HttpResponseRedirect
from .models import Prodotto, Ordine, OrdineProdotto, Carrello
from .forms import *
from django.db.models import F,Sum,Q
from django.views.generic import ListView

# Create your views here.
class ProductListView(ListView):
    model = Prodotto
    template_name = 'home.html'
    context_object_name = 'prodottiInVendita'

    def get_queryset(self):
        queryset = Prodotto.objects.filter(visibile=True)
        ricerca = self.request.GET.get("ricerca", "")
        if ricerca:
            queryset = queryset.filter(
                Q(nome__icontains=ricerca) |
                Q(descrizione__icontains=ricerca) |
                Q(categoria__icontains=ricerca)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = cercaProdottoForm(self.request.GET or None)
        return context

def cliente(response):
    return render(response, 'cliente.html', {})

def aggiungiProdotto(request):
    if request.method == "POST":
        form = aggiungiProdottoForm(request.POST)

        if form.is_valid():
            n = form.cleaned_data["nome"]
            d = form.cleaned_data["descrizione"]
            p = form.cleaned_data["prezzo"]
            c = form.cleaned_data["categoria"]
            nuovoP = Prodotto(nome=n, descrizione=d, prezzo=p, categoria=c)
            nuovoP.save()
            return HttpResponseRedirect("/gestioneProdotti")
        else:
            print("Form non valido")
    else:
        form = aggiungiProdottoForm()
    return render(request, "aggiungiProdotto.html", {"form":form})

def gestioneProdotti(request):
    if not request.user.is_superuser:
        return HttpResponseRedirect("/login")
    if request.method == "POST":
        idP = request.POST.get("idP")
        pDaGestire = Prodotto.objects.get(id=idP)
        if "aggiungiProdottoForm" in request.POST:
            return HttpResponseRedirect("/aggiungiProdotti")
        if "modificaProdottoForm" in request.POST:
            form = modificaProdottoForm()
            return render(request, 'modificaProdotto.html', {"pDaGestire": pDaGestire, "form": form})
        if "annullaModifiche" in request.POST:
            return HttpResponseRedirect("/gestioneProdotti")
        if "salvaModifiche" in request.POST:
            form = modificaProdottoForm(request.POST)
            if form.is_valid():
                if form.cleaned_data["nuovoNome"]:
                    pDaGestire.nome = form.cleaned_data["nuovoNome"]
                    print("nome modificato in: "+form.cleaned_data["nuovoNome"])
                if form.cleaned_data["nuovaDescrizione"] != "":
                    pDaGestire.descrizione = form.cleaned_data["nuovaDescrizione"]
                if form.cleaned_data["nuovoPrezzo"] != "":
                    pDaGestire.prezzo = form.cleaned_data["nuovoPrezzo"]
                pDaGestire.save()
            return HttpResponseRedirect("/gestioneProdotti")
        if "modificaVisibilita" in request.POST:
            pDaGestire.visibile = not pDaGestire.visibile
            pDaGestire.save()
            return HttpResponseRedirect("/gestioneProdotti")
        if "eliminaProdotto" in request.POST:
            pDaGestire.delete()
            return HttpResponseRedirect("/gestioneProdotti")
    prodotti = Prodotto.objects.all()
    return render(request, "gestioneProdotti.html", {"prodotti": prodotti})

def gestioneAcquisto(request):
    if request.user.is_authenticated:
        if request.method == 'POST':

            idP = request.POST.get("idP")
            quantita_str = request.POST.get("quantita", "1")
            prodottoDaGestire = Prodotto.objects.get(id=idP)
            quantita = int(quantita_str)
            if quantita <= 0:
                quantita = 1
            print("GESTIONE ACQUISTO")
            print("idProdotto: " + str(idP))
            print("quantita: " + str(quantita))

            if 'aggiungiAlCarrelloButton' in request.POST:
                for prodotto in Carrello.objects.filter(cliente=request.user):
                    if prodotto.prodotto.id == int(idP):
                        prodotto.quantita += int(quantita)
                        prodotto.save()
                        return HttpResponseRedirect("/home")
                nuovoProdottoCarrello = Carrello(prodotto=prodottoDaGestire, cliente=request.user, quantita=quantita)
                nuovoProdottoCarrello.save()
                return HttpResponseRedirect("/home")
    else:
        return HttpResponseRedirect("/login")

def aggiungiAlCarrello(request):
    if request.user.is_authenticated:

        if "aggiungiAlCarrelloButton" in request.POST:
            idP = request.POST.get("idP")
            quantita_str = request.POST.get("quantita", "1")

            quantita = int(quantita_str)
            if quantita <= 0:
                quantita = 1

            for prod in Carrello.objects.filter(cliente=request.user):
                if prod.prodotto.id == int(idP):
                    prod.quantita += quantita
                    prod.save()
                    return HttpResponseRedirect("/home")
            nuovoProd = Carrello(prodotto=Prodotto.objects.get(id=idP), cliente=request.user, quantita=quantita)
            nuovoProd.save()
            return HttpResponseRedirect("/home")
    else:
        return HttpResponseRedirect("/login")

def effettuaOrdine(request):
    nuovoOrdine = Ordine(cliente=request.user)
    nuovoOrdine.save()
    prodCarrello = Carrello.objects.filter(cliente=request.user)
    tot = (prodCarrello.annotate(subtotale=F("quantita") * F("prodotto__prezzo")).aggregate(totale=Sum("subtotale"))["totale"]) or 0
    for prod in prodCarrello:
        nuovoProdOrd = OrdineProdotto(prodotto=prod.prodotto, ordine=nuovoOrdine, quantita=prod.quantita)
        nuovoProdOrd.save()
        prod.delete()
    return render(request, "pagamento.html", {"nuovoOrdine": nuovoOrdine, "totale":tot})

def revisioneOrdine(request):
    if request.method == "POST":
        idP = request.POST.get("idP")
        if "diminuisciQuantita" in request.POST:
            pDaGestire = Carrello.objects.get(id=idP)
            pDaGestire.quantita -= 1
            pDaGestire.save()
            if pDaGestire.quantita==0:
                pDaGestire.delete()
                return HttpResponseRedirect("/carrello")
        if "aumentaQuantita" in request.POST:
            pDaGestire = Carrello.objects.get(id=idP)
            pDaGestire.quantita += 1
            pDaGestire.save()
        if "rimuoviOggetto" in request.POST:
            pDaGestire = Carrello.objects.get(id=idP)
            pDaGestire.delete()
            return HttpResponseRedirect("/carrello")
        prodCarrello = Carrello.objects.filter(cliente=request.user)
        tot = prodCarrello.annotate(subtotale=F("quantita")*F("prodotto__prezzo")).aggregate(Sum("subtotale"))["subtotale__sum"] or 0

        return render(request, "revisioneOrdine.html", {"daRevisionare":prodCarrello, "totale":tot})

def gestioneCarrello(request):
    if request.user.is_authenticated:

        idP = request.POST.get("idP")
        if 'diminuisciQuantita' in request.POST:
            prodottoDaModificare = Carrello.objects.get(id=idP)
            prodottoDaModificare.quantita -= 1
            if prodottoDaModificare.quantita == 0:
                prodottoDaModificare.delete()
                return HttpResponseRedirect("/carrello")
            prodottoDaModificare.save()
            return HttpResponseRedirect("/carrello")
        if 'aumentaQuantita' in request.POST:
            prodottoDaModificare = Carrello.objects.get(id=idP)
            prodottoDaModificare.quantita += 1
            prodottoDaModificare.save()
        if 'rimuoviOggetto' in request.POST:
            prodottoDaModificare = Carrello.objects.get(id=idP)
            prodottoDaModificare.delete()
            return HttpResponseRedirect("/carrello")

        carrelloCliente = Carrello.objects.filter(cliente=request.user).select_related('prodotto')
        totale = carrelloCliente.annotate(subtotale=F('quantita') * F('prodotto__prezzo')).aggregate(Sum('subtotale'))['subtotale__sum'] or 0
        return render(request, 'carrello.html', {"carrelloCliente": carrelloCliente, "totale": totale})
    else:
        return render(request, 'carrello.html', {})

def salvaPagamento(request):
    if request.method == "POST":
        idOrdine = request.POST.get("idOrdine")
        daPagare = Ordine.objects.get(id=idOrdine)
        daPagare.carta = request.POST.get("carta")
        print("Numero carta: ", daPagare.carta)
        daPagare.cvv = request.POST.get("cvv")
        daPagare.save()
        return HttpResponseRedirect("/home")

def vediOrdine(request):
    if request.method == "POST":
        idOrdine = request.POST.get("idOrdine")
        daVedere = Ordine.objects.get(id=idOrdine)
        prodOrd = OrdineProdotto.objects.prefetch_related('prodotto').filter(ordine=idOrdine)
        tot = prodOrd.annotate(subtotale=F('quantita') * F('prodotto__prezzo')).aggregate(Sum('subtotale'))['subtotale__sum'] or 0
        return render(request ,  "vediOrdine.html" , {"ordineDaVedere": daVedere , "prodottiOrdine" : prodOrd , "totale": tot})
    else:
        return render(request, "vediOrdine.html", {})

def cronologiaOrdini(request):
    ordini = Ordine.objects.filter(cliente=request.user)
    return render(request ,  "cronologiaOrdini.html" , {"ordini":ordini })