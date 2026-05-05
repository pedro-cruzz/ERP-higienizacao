from service.views.catalogo import catalogo, listar_clientes, listar_leads
from service.views.comum import inicio, teste
from service.views.orcamentos import (
    aprovar_orcamento,
    detalhe_orcamento,
    gerar_orcamento_pdf,
    novo_orcamento,
)
from service.views.produtos import novo_produto

__all__ = [
    "aprovar_orcamento",
    "catalogo",
    "detalhe_orcamento",
    "gerar_orcamento_pdf",
    "inicio",
    "listar_clientes",
    "listar_leads",
    "novo_orcamento",
    "novo_produto",
    "teste",
]
