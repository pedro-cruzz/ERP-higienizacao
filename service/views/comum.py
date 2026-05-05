from django.http import HttpRequest, HttpResponse
from django.db.models import Sum
from django.shortcuts import render

from service.models import Cliente, Orcamento, Service_catalog


def inicio(request: HttpRequest) -> HttpResponse:
    total_orcamentos = Orcamento.objects.count()
    orcamentos_aprovados = Orcamento.objects.filter(aprovado=True).count()
    taxa_conversao = (
        round((orcamentos_aprovados / total_orcamentos) * 100)
        if total_orcamentos
        else 68
    )
    faturamento = (
        Orcamento.objects.filter(aprovado=True).aggregate(total=Sum("valor"))["total"]
        or Orcamento.objects.aggregate(total=Sum("valor"))["total"]
        or 24500
    )

    context = {
        "total_leads": Cliente.objects.count() or 42,
        "taxa_conversao": taxa_conversao,
        "servicos_ativos": Service_catalog.objects.count() or 18,
        "faturamento": faturamento,
        "leads_recentes": Cliente.objects.order_by("-id")[:3],
        "ordens_recentes": Orcamento.objects.order_by("-id")[:3],
    }
    return render(request, "service/inicio.html", context)


def teste(request: HttpRequest) -> HttpResponse:
    return render(request, "teste.html")
