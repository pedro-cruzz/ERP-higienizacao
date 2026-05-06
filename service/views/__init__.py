from service.views.catalogo import (
    catalogo,
    deletar_cliente,
    listar_clientes,
    listar_leads,
    nova_categoria,
    novo_lead,
)
from service.views.comum import inicio, teste
from service.views.orcamentos import (
    aprovar_orcamento,
    buscar_endereco_cep,
    cadastrar_cliente_orcamento,
    concluir_orcamento,
    deletar_orcamento,
    detalhe_orcamento,
    gerar_orcamento_pdf,
    listar_orcamentos,
    novo_orcamento,
)
from service.views.produtos import deletar_produto, editar_produto, novo_produto

__all__ = [
    "aprovar_orcamento",
    "buscar_endereco_cep",
    "cadastrar_cliente_orcamento",
    "catalogo",
    "concluir_orcamento",
    "deletar_cliente",
    "deletar_orcamento",
    "deletar_produto",
    "detalhe_orcamento",
    "editar_produto",
    "gerar_orcamento_pdf",
    "inicio",
    "listar_clientes",
    "listar_leads",
    "listar_orcamentos",
    "nova_categoria",
    "novo_lead",
    "novo_orcamento",
    "novo_produto",
    "teste",
]
