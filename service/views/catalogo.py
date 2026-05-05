from django.contrib import messages
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from service.forms import ClienteForm
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
            | Q(status__icontains=busca)
        )

    context = {
        "busca": busca,
        "clientes": clientes,
        "total_clientes": clientes.count(),
    }
    return render(request, "service/clientes.html", context)


def novo_lead(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ClienteForm(request.POST)
        if form.is_valid():
            lead = form.save()
            messages.success(request, f"Lead '{lead.name}' cadastrado com sucesso.")
            return redirect("clientes")
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
