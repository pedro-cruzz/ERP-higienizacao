from django.urls import path

from service.views import (
    aprovar_orcamento,
    cadastrar_cliente_orcamento,
    catalogo,
    concluir_orcamento,
    deletar_cliente,
    deletar_orcamento,
    detalhe_orcamento,
    gerar_orcamento_pdf,
    inicio,
    listar_clientes,
    listar_orcamentos,
    novo_lead,
    novo_orcamento,
    novo_produto,
    teste,
)

urlpatterns = [
    path("", inicio, name="inicio"),
    path("teste/", teste, name="teste"),
    path("catalogo/", catalogo, name="catalogo"),
    path("clientes/", listar_clientes, name="clientes"),
    path("clientes/novo/", novo_lead, name="novo_lead"),
    path("clientes/<int:pk>/deletar/", deletar_cliente, name="deletar_cliente"),
    path("catalogo/novo/", novo_produto, name="novo_produto"),
    path("orcamentos/", listar_orcamentos, name="orcamentos"),
    path("orcamentos/novo/", novo_orcamento, name="novo_orcamento"),
    path("orcamentos/<int:pk>/", detalhe_orcamento, name="orcamento_detalhe"),
    path("orcamentos/<int:pk>/pdf/", gerar_orcamento_pdf, name="gerar_orcamento_pdf"),
    path("orcamentos/<int:pk>/concluir/", concluir_orcamento, name="concluir_orcamento"),
    path(
        "orcamentos/<int:pk>/cadastrar-cliente/",
        cadastrar_cliente_orcamento,
        name="cadastrar_cliente_orcamento",
    ),
    path("orcamentos/<int:pk>/aprovar/", aprovar_orcamento, name="aprovar_orcamento"),
    path("orcamentos/<int:pk>/deletar/", deletar_orcamento, name="deletar_orcamento"),
]
