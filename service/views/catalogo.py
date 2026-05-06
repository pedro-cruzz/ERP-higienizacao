from django.contrib import messages
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from service.forms import ClienteForm
from service.models import Cliente, Service_catalog


def _lead_status_class(status: str) -> str:
    return {
        Cliente.Status.NOVO: "status-blue",
        Cliente.Status.CONTATADO: "status-yellow",
        Cliente.Status.AGUARDANDO: "status-gray",
        Cliente.Status.CONVERTIDO: "status-soft-blue",
    }.get(status, "status-gray")


def catalogo(request: HttpRequest) -> HttpResponse:
    busca = request.GET.get("q", "").strip()
    itens = Service_catalog.objects.order_by("name")

    if busca:
        itens = itens.filter(
            Q(name__icontains=busca)
            | Q(tipo__icontains=busca)
            | Q(descricao__icontains=busca)
        )

    context = {
        "busca": busca,
        "itens": itens,
        "total_itens": itens.count(),
    }
    return render(request, "service/catalogo.html", context)


def listar_clientes(request: HttpRequest) -> HttpResponse:
    busca = request.GET.get("q", "").strip()
    clientes = Cliente.objects.order_by("name")

    if busca:
        clientes = clientes.filter(
            Q(name__icontains=busca)
            | Q(email__icontains=busca)
            | Q(telefone__icontains=busca)
            | Q(status__icontains=busca)
        )

    context = {
        "busca": busca,
        "clientes": clientes,
        "total_clientes": clientes.count(),
    }
    return render(request, "service/clientes.html", context)


def listar_leads(request: HttpRequest) -> HttpResponse:
    busca = request.GET.get("q", "").strip()
    clientes = Cliente.objects.order_by("-created_at", "-id")

    if busca:
        clientes = clientes.filter(
            Q(name__icontains=busca)
            | Q(email__icontains=busca)
            | Q(telefone__icontains=busca)
            | Q(status__icontains=busca)
        )

    origem_cycle = ["WhatsApp", "Instagram", "Indicação"]
    leads = []
    for index, cliente in enumerate(clientes[:5]):
        leads.append(
            {
                "name": cliente.name,
                "telefone": cliente.telefone or cliente.email or "-",
                "status": cliente.get_status_display(),
                "status_class": _lead_status_class(cliente.status),
                "origem": origem_cycle[index % len(origem_cycle)],
                "data": cliente.created_at.strftime("%d/%m/%Y"),
            }
        )

    if not leads and not busca:
        leads = [
            {
                "name": "Maria Santos",
                "telefone": "(11) 98765-4321",
                "status": "Novo",
                "status_class": "status-blue",
                "origem": "WhatsApp",
                "data": "29/04/2026",
            },
            {
                "name": "Carlos Oliveira",
                "telefone": "(11) 97654-3210",
                "status": "Contatado",
                "status_class": "status-yellow",
                "origem": "Instagram",
                "data": "28/04/2026",
            },
            {
                "name": "Ana Costa",
                "telefone": "(11) 96543-2109",
                "status": "Aguardando",
                "status_class": "status-gray",
                "origem": "Indicação",
                "data": "28/04/2026",
            },
            {
                "name": "Paulo Mendes",
                "telefone": "(11) 95432-1098",
                "status": "Novo",
                "status_class": "status-blue",
                "origem": "WhatsApp",
                "data": "27/04/2026",
            },
            {
                "name": "Fernanda Rocha",
                "telefone": "(11) 94321-0987",
                "status": "Contatado",
                "status_class": "status-yellow",
                "origem": "Instagram",
                "data": "27/04/2026",
            },
        ]

    context = {
        "busca": busca,
        "leads": leads,
        "total_leads": clientes.count() if busca or Cliente.objects.exists() else len(leads),
    }
    return render(request, "service/leads.html", context)


def novo_lead(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ClienteForm(request.POST)
        if form.is_valid():
            lead = form.save()
            messages.success(request, f"Lead '{lead.name}' cadastrado com sucesso.")
            return redirect("leads")
    else:
        form = ClienteForm()

    context = {
        "form": form,
        "leads_recentes": Cliente.objects.order_by("-created_at", "-id")[:5],
    }
    return render(request, "service/lead_form.html", context)


def deletar_cliente(request: HttpRequest, pk: int) -> HttpResponse:
    if request.method != "POST":
        return redirect("clientes")

    cliente = get_object_or_404(Cliente, pk=pk)
    nome = cliente.name
    cliente.delete()

    messages.success(request, f"Cliente '{nome}' excluido com sucesso.")
    return redirect("clientes")
