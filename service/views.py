from django.contrib import messages
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from service.forms import OrcamentoForm
from service.models import Orcamento, Service_catalog


def inicio(request: HttpRequest) -> HttpResponse:
    return redirect("catalogo")



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


def novo_orcamento(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = OrcamentoForm(request.POST)
        if form.is_valid():
            itens = list(form.cleaned_data["itens"])
            quantidade = form.cleaned_data["quantidade"]
            valor_total = sum(item.valor for item in itens) * quantidade

            orcamento = Orcamento.objects.create(
                name=form.cleaned_data["name"],
                descricao=form.cleaned_data["descricao"] or None,
                quantidade=quantidade,
                valor=valor_total,
            )
            orcamento.itens.set(itens)

            messages.success(request, "Orcamento criado com sucesso.")
            return redirect("orcamento_detalhe", pk=orcamento.pk)
    else:
        form = OrcamentoForm()

    context = {
        "form": form,
        "orcamentos_recentes": Orcamento.objects.prefetch_related("itens").order_by("-id")[:5],
    }
    return render(request, "service/orcamento_form.html", context)


def detalhe_orcamento(request: HttpRequest, pk: int) -> HttpResponse:
    orcamento = get_object_or_404(
        Orcamento.objects.prefetch_related("itens"),
        pk=pk,
    )
    context = {
        "orcamento": orcamento,
        "itens": orcamento.itens.all(),
    }
    return render(request, "service/orcamento_detalhe.html", context)
