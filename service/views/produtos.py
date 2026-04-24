from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from service.forms import ProdutoCatalogoForm
from service.models import Service_catalog


def novo_produto(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ProdutoCatalogoForm(request.POST)
        if form.is_valid():
            produto = form.save()
            messages.success(request, f"Produto '{produto.name}' cadastrado com sucesso.")
            return redirect("catalogo")
    else:
        form = ProdutoCatalogoForm()

    context = {
        "form": form,
        "ultimos_produtos": Service_catalog.objects.order_by("-id")[:5],
    }
    return render(request, "service/produto_form.html", context)
