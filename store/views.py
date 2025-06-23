from django.shortcuts import render
from django.http import HttpResponseRedirect
from store.models import prodotto, ordine, ordineProdotto, carrello
from .forms import *
from django.db.models import F,Sum,Q
from django.views.generic import ListView

# Create your views here.
class ProductListView(ListView):
    model = prodotto
    template_name = 'home.html'
    context_object_name = 'prodottiInVendita'

    def get_queryset(self):
        queryset = prodotto.objects.filter(visibile=True)
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
            nuovoP = prodotto(nome=n, descrizione=d, prezzo=p, categoria=c)
            nuovoP.save()
            return HttpResponseRedirect("gestioneProdotti")
        else:
            print("Form non valido")
    else:
        form = aggiungiProdottoForm()
    return render(request, "aggiungiProdotto.html", {"form":form})

def gestioneProdotti(request):
    prodotti = prodotto.objects.all()
    if request.user.is_superuser:
        if request.method == "POST":
            idP = request.POST.get("idP")
            pDaGestire = prodotto.objects.get(id=idP)
            if "aggiungiProdottoForm" in request.POST:
                return HttpResponseRedirect("aggiungiProdotti")
            if "modificarProdottoForm" in request.POST:
                form = modificaProdottoForm()
                return render(request, 'modificaProdotto.html', {"pDaGestire": pDaGestire, "form": form})
            if "annullaModifiche" in request.POST:
                return render(request, 'gestioneProdotti.html', {"prodotti": prodotti})
            if "salvaModifiche" in request.POST:
                form = modificaProdottoForm(request.POST)
                if form.is_valid():
                    if form.cleaned_data["nuovoNome"] != "":
                        pDaGestire.nome = form.cleaned_data["nuovoNome"]
                        print("nome modificato in: "+form.cleaned_data["nuovoNome"])
                    if form.cleaned_data["nuovaDescrizione"] != "":
                        pDaGestire.descrizione = form.cleaned_data["nuovaDescrizione"]
                    if form.cleaned_data["nuovoPrezzo"] != "":
                        pDaGestire.prezzo = form.cleaned_data["nuovoPrezzo"]
                    pDaGestire.save()
                return render(request, "gestioneProdotti.html", {"prodotti": prodotti})
            if "modificaVisibilità" in request.POST:
                if pDaGestire.visibile:
                    pDaGestire.visibile = False
                else:
                    pDaGestire.visibile = True
                pDaGestire.save()
                return render(request, "gestioneProdotti.html", {"prodotti": prodotti})
            return render(request, "gestioneProdotti.html", {"prodotti": prodotti})
        else:
            return render(request, "gestioneProdotti.html")
    else:
        return HttpResponseRedirect("login")

def gestioneAcquisto(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            idP = request.POST.get("idP")
            quantita = request.POST.get("quantita")
            pDaGestire = prodotto.objects.get(id=idP)
            if quantita == "":
                quantita = 1
            print("Gestione Acquisto")
            print("id prodotto: "+str(idP))
            print("quantita: "+str(quantita))

            if "aggiungiAlCarrelloButton" in request.POST:
                for prod in carrello.objects.filter(cliente=request.user):
                    if prod.prodotto.id == int(idP):
                        prod.quantita += int(quantita)
                        prod.save()
                        return HttpResponseRedirect("home")
                nuovoProd = carrello(prodotto=pDaGestire, cliente=request.user, quantita=quantita)
                nuovoProd.save()
                return HttpResponseRedirect("home")
    else:
        return HttpResponseRedirect("login")

def aggiungiAlCarrello(request):
    if request.user.is_authenticated:
        idP = request.POST.get("idP")
        quantita = request.POST.get("quantita")
        if quantita == "":
            quantita = 1
        if "aggiungiAlCarrelloButton" in request.POST:
            for prod in carrello.objects.filter(cliente=request.user):
                if prod.prodotto.id == int(idP):
                    prod.quantita += int(quantita)
                    prod.save()
                    return HttpResponseRedirect("home")
            nuovoProd = carrello(prodotto=prodotto.objects.get(id=idP), cliente=request.user, quantita=quantita)
            nuovoProd.save()
            return HttpResponseRedirect("home")
    else:
        return HttpResponseRedirect("login")

def effettuaOrdine(request):
    nuovoOrdine = ordine(cliente=request.user)
    nuovoOrdine.save()
    prodCarrello = carrello.objects.filter(cliente=request.user)
    for prod in prodCarrello:
        nuovoProdOrd = ordineProdotto(prodotto=prod.prodotto, ordine=nuovoOrdine, quantita=prod.quantita)
        nuovoProdOrd.save()
        prod.delete()
    return render(request, "pagamento.html", {"nuovoOrdine": nuovoOrdine})

def revisioneOrdine(request):
    if request.method == "POST":
        idP = request.POST.get("idP")
        if "diminuisciQuantita" in request.POST:
            pDaGestire = carrello.objects.get(id=idP)
            pDaGestire.quantita -= 1
            pDaGestire.save()
            if pDaGestire.quantita==0:
                pDaGestire.delete()
                return HttpResponseRedirect("carrello")
        if "aumentaQuantita" in request.POST:
            pDaGestire = carrello.objects.get(id=idP)
            pDaGestire.quantita += 1
            pDaGestire.save()
        if "rimuoviOggetto" in request.POST:
            pDaGestire = carrello.objects.get(id=idP)
            pDaGestire.delete()
            return HttpResponseRedirect("carrello")
        prodCarrello = carrello.objects.filter(cliente=request.user)
        tot = prodCarrello.annotate(subtotale=F("quantita")*F("prodotto__prezzo")).aggregate(Sum("subtotale"))["subtotale__sum"] or 0

        return render(request, "revisioneOrdine.html", {"daRevisionare":prodCarrello, "totale":tot})

def gestioneCarrello(request):
    if request.user.is_authenticated:
        idP = request.POST.get("idP")
        if "diminuisciQuantita" in request.POST:
            pDaGestire = carrello.objects.get(id=idP)
            pDaGestire.quantita -= 1
            pDaGestire.save()
            if pDaGestire.quantita==0:
                pDaGestire.delete()
                return HttpResponseRedirect("carrello")
        if "aumentaQuantita" in request.POST:
            pDaGestire = carrello.objects.get(id=idP)
            pDaGestire.quantita += 1
            pDaGestire.save()
        if "rimuoviOggetto" in request.POST:
            pDaGestire = carrello.objects.get(id=idP)
            pDaGestire.delete()
            return HttpResponseRedirect("carrello")
        carrelloCliente = carrello.objects.filter(cliente=request.user).select_related("prodotto")
        tot =carrelloCliente.annotate(subtotale=F('quantita') * F('prodotto__prezzo')).aggregate(Sum('subtotale'))['subtotale__sum'] or 0
        return render(request, 'carrello.html', {"carrelloCliente": carrelloCliente, "totale": tot})
    else:
        return render(request, 'carrello.html', {})

def salvaPagamento(request):
    if request.method == "POST":
        idOrd = request.POST.get("idOrd")
        daPagare = ordine.objects.get(id=idOrd)
        daPagare.carta = request.POST.get("carta")
        print("Numero carta: ", daPagare.carta)
        daPagare.cvv = request.POST.get("cvv")
        daPagare.save()
        return HttpResponseRedirect("home")

def vediOrdine(request):
    if request.method == "POST":
        idOrd = request.POST.get("idOrd")
        daVedere = ordine.objects.get(id=idOrd)
        prodOrd = ordineProdotto.objects.prefetch_related('prodotto').filter(ordine=idOrd)
        tot = prodOrd.annotate(subtotale=F('quantita') * F('prodotto__prezzo')).aggregate(Sum('subtotale'))['subtotale__sum'] or 0
        return render(request ,  "vediOrdine.html" , {"ordineDaVedere": daVedere , "prodottiOrdine" : prodOrd , "totale": tot})
    else:
        return render(request, "vediOrdine.html", {})

def cronologiaOrdini(request):
    ordini = ordine.objects.filter(cliente=request.user)
    return render(request ,  "cronologiaOrdini.html" , {"ordini":ordini })