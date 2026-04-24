from django.db import models


class Service_catalog(models.Model):
    name = models.CharField(max_length=100, unique=True, null=False)
    tempo = models.CharField(max_length=100, null=True)
    tipo = models.CharField(max_length=100, null=True)
    id = models.AutoField(primary_key=True)
    valor = models.FloatField(null=False)
    descricao = models.TextField(null=True)
    formato = models.CharField(max_length=100, null=True)
    tamanho = models.CharField(max_length=100, null=True)
    largura = models.CharField(max_length=100, null=True)
    comprimento = models.CharField(max_length=100, null=True)
    tecido = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.name


class Orcamento(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=False)
    email = models.EmailField(null=True, blank=True)
    telefone = models.CharField(max_length=20, null=True, blank=True)
    endereco = models.CharField(max_length=200, null=True, blank=True)
    valor = models.FloatField(null=False)
    descricao = models.TextField(null=True)
    quantidade = models.IntegerField(null=False)
    itens = models.ManyToManyField(Service_catalog, related_name="orcamento_items")
    aprovado = models.BooleanField(default=False)
    cliente = models.ForeignKey(
        "Cliente",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orcamentos",
    )

    class Meta:
        db_table = "service_orcamento"

    def __str__(self):
        return self.name
    
class Cliente(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=False)
    email = models.EmailField(null=False)
    telefone = models.CharField(max_length=20, null=True, blank=True)
    endereco = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name
