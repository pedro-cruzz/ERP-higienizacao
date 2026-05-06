from django.contrib import admin

from service.models import CategoriaCatalogo, Cliente, Orcamento, Service_catalog


@admin.register(CategoriaCatalogo)
class CategoriaCatalogoAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name", "descricao")


@admin.register(Service_catalog)
class ServiceCatalogAdmin(admin.ModelAdmin):
    list_display = ("name", "categoria", "tipo", "valor")
    list_filter = ("categoria",)
    search_fields = ("name", "tipo", "categoria__name")


@admin.register(Orcamento)
class OrcamentoAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "valor", "quantidade", "aprovado", "cliente")
    list_filter = ("aprovado",)
    search_fields = ("name", "email")


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "telefone")
    search_fields = ("name", "email")
