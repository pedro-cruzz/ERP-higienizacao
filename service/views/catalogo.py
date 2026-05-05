from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from service.models import Cliente, Service_catalog


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
        )

    context = {
        "busca": busca,
        "clientes": clientes,
        "total_clientes": clientes.count(),
    }
    return render(request, "service/clientes.html", context)


def listar_leads(request: HttpRequest) -> HttpResponse:
    busca = request.GET.get("q", "").strip()
    clientes = Cliente.objects.order_by("-id")

    if busca:
        clientes = clientes.filter(
            Q(name__icontains=busca)
            | Q(email__icontains=busca)
            | Q(telefone__icontains=busca)
        )

    status_cycle = [
        ("Novo", "status-blue"),
        ("Contatado", "status-yellow"),
        ("Aguardando", "status-gray"),
    ]
    origem_cycle = ["WhatsApp", "Instagram", "Indicação"]
    date_cycle = ["29/04/2026", "28/04/2026", "28/04/2026"]

    leads = []
    for index, cliente in enumerate(clientes[:5]):
        status, status_class = status_cycle[index % len(status_cycle)]
        leads.append(
            {
                "name": cliente.name,
                "telefone": cliente.telefone or cliente.email or "-",
                "status": status,
                "status_class": status_class,
                "origem": origem_cycle[index % len(origem_cycle)],
                "data": date_cycle[index % len(date_cycle)],
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
