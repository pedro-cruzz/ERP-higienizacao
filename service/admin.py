from django.contrib import admin

from service.models import Cliente, Orcamento, Service_catalog


@admin.register(Service_catalog)
class ServiceCatalogAdmin(admin.ModelAdmin):
    list_display = ("name", "tipo", "valor")
    search_fields = ("name", "tipo")


@admin.register(Orcamento)
class OrcamentoAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "valor", "quantidade", "aprovado", "cliente")
    list_filter = ("aprovado",)
    search_fields = ("name", "email")


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "telefone")
    search_fields = ("name", "email")
