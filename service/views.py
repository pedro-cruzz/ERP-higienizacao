from django.contrib import messages
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from service.forms import OrcamentoForm, ProdutoCatalogoForm
from service.models import Cliente, Orcamento, Service_catalog


def inicio(request: HttpRequest) -> HttpResponse:
    return redirect("catalogo")


def teste(request: HttpRequest) -> HttpResponse:
    return render(request, "teste.html")


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


def novo_orcamento(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = OrcamentoForm(request.POST)
        if form.is_valid():
            itens = list(form.cleaned_data["itens"])
            quantidade = form.cleaned_data["quantidade"]
            valor_total = sum(item.valor for item in itens) * quantidade

            orcamento = Orcamento.objects.create(
                name=form.cleaned_data["name"],
                telefone=form.cleaned_data["telefone"] or None,
                endereco=form.cleaned_data["endereco"] or None,
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
        Orcamento.objects.prefetch_related("itens", "cliente"),
        pk=pk,
    )
    context = {
        "orcamento": orcamento,
        "itens": orcamento.itens.all(),
    }
    return render(request, "service/orcamento_detalhe.html", context)


def aprovar_orcamento(request: HttpRequest, pk: int) -> HttpResponse:
    if request.method != "POST":
        return redirect("orcamento_detalhe", pk=pk)

    orcamento = get_object_or_404(Orcamento, pk=pk)

    if not orcamento.email:
        messages.error(
            request,
            "Este orcamento precisa de um email para criar o cadastro do cliente.",
        )
        return redirect("orcamento_detalhe", pk=pk)

    cliente = Cliente.objects.filter(email=orcamento.email).first()
    if cliente is None:
        cliente = Cliente.objects.create(
            name=orcamento.name,
            email=orcamento.email,
            telefone=orcamento.telefone,
            endereco=orcamento.endereco,
        )
    else:
        cliente.name = orcamento.name
        cliente.telefone = orcamento.telefone
        cliente.endereco = orcamento.endereco
        cliente.save()

    orcamento.cliente = cliente
    orcamento.aprovado = True
    orcamento.save(update_fields=["cliente", "aprovado"])

    messages.success(
        request,
        "Orcamento aprovado e cliente vinculado com sucesso.",
    )
    return redirect("orcamento_detalhe", pk=pk)
