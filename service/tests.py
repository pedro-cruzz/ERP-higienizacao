from django.test import TestCase
from django.urls import reverse

from service.models import Cliente, Orcamento, Service_catalog


class ServiceViewsTests(TestCase):
    def setUp(self):
        self.item_a = Service_catalog.objects.create(
            name="Banner 1x1",
            tipo="Impressao",
            valor=120.0,
            descricao="Banner em lona",
        )
        self.item_b = Service_catalog.objects.create(
            name="Adesivo vitrine",
            tipo="Recorte",
            valor=80.0,
            descricao="Adesivo para vitrine",
        )

    def test_catalogo_retorna_ok(self):
        response = self.client.get(reverse("catalogo"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Catalogo")
        self.assertContains(response, self.item_a.name)

    def test_lista_clientes_retorna_ok(self):
        Cliente.objects.create(
            name="Maria Cliente",
            email="maria@teste.com",
            telefone="11911112222",
            endereco="Rua das Flores, 12",
        )

        response = self.client.get(reverse("clientes"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Clientes")
        self.assertContains(response, "Maria Cliente")

    def test_inicio_exibe_metricas_reais(self):
        lead = Cliente.objects.create(
            name="Lead Dashboard",
            email="lead@teste.com",
            telefone="11922223333",
        )
        orcamento = Orcamento.objects.create(
            name="Cliente Dashboard",
            email="dashboard@teste.com",
            quantidade=1,
            valor=120.0,
            aprovado=True,
            cliente=lead,
        )
        orcamento.itens.set([self.item_a])

        response = self.client.get(reverse("inicio"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Lead Dashboard")
        self.assertContains(response, "Cliente Dashboard")
        self.assertContains(response, "100%")

    def test_cria_lead(self):
        response = self.client.post(
            reverse("novo_lead"),
            {
                "name": "Lead Novo",
                "email": "novo@teste.com",
                "telefone": "11933334444",
                "endereco": "Rua Lead, 10",
                "status": Cliente.Status.CONTATADO,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Cliente.objects.filter(email="novo@teste.com").exists())

    def test_lista_orcamentos_retorna_ok(self):
        orcamento = Orcamento.objects.create(
            name="Cliente Lista",
            email="lista@teste.com",
            quantidade=1,
            valor=120.0,
            descricao="Busca por lista",
        )
        orcamento.itens.set([self.item_a])

        response = self.client.get(reverse("orcamentos"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cliente Lista")
        self.assertContains(response, "120.00")

    def test_deleta_cliente_sem_apagar_orcamento(self):
        cliente = Cliente.objects.create(
            name="Cliente Remover",
            email="remover@teste.com",
        )
        orcamento = Orcamento.objects.create(
            name="Cliente Remover",
            email="remover@teste.com",
            quantidade=1,
            valor=120.0,
            cliente=cliente,
        )
        orcamento.itens.set([self.item_a])

        response = self.client.post(reverse("deletar_cliente", args=[cliente.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Cliente.objects.filter(pk=cliente.pk).exists())
        orcamento.refresh_from_db()
        self.assertIsNone(orcamento.cliente)

    def test_deleta_orcamento(self):
        orcamento = Orcamento.objects.create(
            name="Orcamento Remover",
            email="orcamento-remover@teste.com",
            quantidade=1,
            valor=120.0,
        )
        orcamento.itens.set([self.item_a])

        response = self.client.post(reverse("deletar_orcamento", args=[orcamento.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Orcamento.objects.filter(pk=orcamento.pk).exists())

    def test_cria_produto_no_catalogo(self):
        response = self.client.post(
            reverse("novo_produto"),
            {
                "name": "Faixa promocional",
                "tipo": "Impressao",
                "valor": 59.9,
                "descricao": "Faixa em lona com acabamento.",
                "tempo": "1 dia util",
                "formato": "3x0,7 m",
                "tamanho": "Grande",
                "largura": "70 cm",
                "comprimento": "300 cm",
                "tecido": "Lona",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Service_catalog.objects.filter(name="Faixa promocional").exists())

    def test_cria_orcamento_com_total(self):
        response = self.client.post(
            reverse("novo_orcamento"),
            {
                "name": "Cliente Teste",
                "email": "cliente@teste.com",
                "telefone": "11999999999",
                "endereco": "Rua Teste, 123",
                "descricao": "Pedido inicial",
                "quantidade": 2,
                "itens": [self.item_a.pk, self.item_b.pk],
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Orcamento.objects.count(), 1)

        orcamento = Orcamento.objects.get()
        self.assertEqual(orcamento.valor, 400.0)
        self.assertEqual(orcamento.quantidade, 2)
        self.assertEqual(orcamento.email, "cliente@teste.com")

    def test_conclui_orcamento_sem_criar_cliente(self):
        orcamento = Orcamento.objects.create(
            name="Cliente Concluir",
            email="concluir@teste.com",
            telefone="11988887777",
            endereco="Rua Concluir, 10",
            quantidade=1,
            valor=120.0,
            descricao="Teste de conclusao",
        )
        orcamento.itens.set([self.item_a])

        response = self.client.post(reverse("concluir_orcamento", args=[orcamento.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Cliente.objects.count(), 0)

        orcamento.refresh_from_db()
        self.assertTrue(orcamento.aprovado)
        self.assertIsNone(orcamento.cliente)

    def test_cadastra_cliente_do_orcamento_sem_concluir(self):
        orcamento = Orcamento.objects.create(
            name="Cliente Cadastrado",
            email="cadastrado@teste.com",
            telefone="11988887777",
            endereco="Rua Cadastro, 10",
            quantidade=1,
            valor=120.0,
            descricao="Teste de cadastro",
        )
        orcamento.itens.set([self.item_a])

        response = self.client.post(reverse("cadastrar_cliente_orcamento", args=[orcamento.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Cliente.objects.count(), 1)

        orcamento.refresh_from_db()
        cliente = Cliente.objects.get()
        self.assertFalse(orcamento.aprovado)
        self.assertEqual(orcamento.cliente, cliente)
        self.assertEqual(cliente.email, "cadastrado@teste.com")

    def test_aprova_orcamento_e_cria_cliente_por_rota_legada(self):
        orcamento = Orcamento.objects.create(
            name="Cliente Aprovado",
            email="aprovado@teste.com",
            telefone="11988887777",
            endereco="Rua Aprovada, 10",
            quantidade=1,
            valor=120.0,
            descricao="Teste de aprovacao",
        )
        orcamento.itens.set([self.item_a])

        response = self.client.post(reverse("aprovar_orcamento", args=[orcamento.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Cliente.objects.count(), 1)

        orcamento.refresh_from_db()
        cliente = Cliente.objects.get()
        self.assertTrue(orcamento.aprovado)
        self.assertEqual(orcamento.cliente, cliente)
        self.assertEqual(cliente.email, "aprovado@teste.com")

    def test_gera_pdf_do_orcamento(self):
        orcamento = Orcamento.objects.create(
            name="Cliente PDF",
            email="pdf@teste.com",
            telefone="11977776666",
            endereco="Rua PDF, 100",
            quantidade=1,
            valor=120.0,
            descricao="Teste de PDF",
        )
        orcamento.itens.set([self.item_a, self.item_b])

        response = self.client.get(reverse("gerar_orcamento_pdf", args=[orcamento.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertIn(f'orcamento-{orcamento.pk}.pdf', response["Content-Disposition"])
        self.assertTrue(response.content.startswith(b"%PDF"))
