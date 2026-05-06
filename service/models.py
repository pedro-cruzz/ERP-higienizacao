from django.db import models


class CategoriaCatalogo(models.Model):
    name = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Service_catalog(models.Model):
    name = models.CharField(max_length=100, unique=True, null=False)
    tempo = models.CharField(max_length=100, null=True)
    tipo = models.CharField(max_length=100, null=True)
    categoria = models.ForeignKey(
        CategoriaCatalogo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="itens",
    )
    id = models.AutoField(primary_key=True)
    valor = models.FloatField(null=False)
    descricao = models.TextField(null=True)
    formato = models.CharField(max_length=100, null=True)
    tamanho = models.CharField(max_length=100, null=True)
    largura = models.CharField(max_length=100, null=True)
    comprimento = models.CharField(max_length=100, null=True)
    tecido = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def categoria_nome(self):
        return self.categoria.name if self.categoria else self.tipo


class Orcamento(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=False)
    email = models.EmailField(null=True, blank=True)
    telefone = models.CharField(max_length=20, null=True, blank=True)
    endereco = models.CharField(max_length=255, null=True, blank=True)
    cep = models.CharField(max_length=9, null=True, blank=True)
    logradouro = models.CharField(max_length=120, null=True, blank=True)
    numero = models.CharField(max_length=20, null=True, blank=True)
    complemento = models.CharField(max_length=120, null=True, blank=True)
    bairro = models.CharField(max_length=120, null=True, blank=True)
    cidade = models.CharField(max_length=120, null=True, blank=True)
    uf = models.CharField(max_length=2, null=True, blank=True)
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "service_orcamento"

    def __str__(self):
        return self.name


class Cliente(models.Model):
    class Status(models.TextChoices):
        NOVO = "novo", "Novo"
        CONTATADO = "contatado", "Contatado"
        AGUARDANDO = "aguardando", "Aguardando"
        CONVERTIDO = "convertido", "Convertido"

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=False)
    email = models.EmailField(null=False)
    telefone = models.CharField(max_length=20, null=True, blank=True)
    endereco = models.CharField(max_length=255, null=True, blank=True)
    cep = models.CharField(max_length=9, null=True, blank=True)
    logradouro = models.CharField(max_length=120, null=True, blank=True)
    numero = models.CharField(max_length=20, null=True, blank=True)
    complemento = models.CharField(max_length=120, null=True, blank=True)
    bairro = models.CharField(max_length=120, null=True, blank=True)
    cidade = models.CharField(max_length=120, null=True, blank=True)
    uf = models.CharField(max_length=2, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NOVO,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
