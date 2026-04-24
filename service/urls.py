from django.urls import path

from service.views import (
    aprovar_orcamento,
    catalogo,
    detalhe_orcamento,
    inicio,
    listar_clientes,
    novo_orcamento,
    novo_produto,
    teste,
)

urlpatterns = [
    path("", inicio, name="inicio"),
    path("teste/", teste, name="teste"),
    path("catalogo/", catalogo, name="catalogo"),
    path("clientes/", listar_clientes, name="clientes"),
    path("catalogo/novo/", novo_produto, name="novo_produto"),
    path("orcamentos/novo/", novo_orcamento, name="novo_orcamento"),
    path("orcamentos/<int:pk>/", detalhe_orcamento, name="orcamento_detalhe"),
    path("orcamentos/<int:pk>/aprovar/", aprovar_orcamento, name="aprovar_orcamento"),
]
