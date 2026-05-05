from service.views.catalogo import catalogo, deletar_cliente, listar_clientes, novo_lead
from service.views.comum import inicio, teste
from service.views.orcamentos import (
    aprovar_orcamento,
    cadastrar_cliente_orcamento,
    concluir_orcamento,
    deletar_orcamento,
    detalhe_orcamento,
    gerar_orcamento_pdf,
    listar_orcamentos,
    novo_orcamento,
)
from service.views.produtos import novo_produto

__all__ = [
    "aprovar_orcamento",
    "cadastrar_cliente_orcamento",
    "catalogo",
    "concluir_orcamento",
    "deletar_cliente",
    "deletar_orcamento",
    "detalhe_orcamento",
    "gerar_orcamento_pdf",
    "inicio",
    "listar_clientes",
    "listar_orcamentos",
    "novo_lead",
    "novo_orcamento",
    "novo_produto",
    "teste",
]
