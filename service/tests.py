from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from service.models import CategoriaCatalogo, Cliente, Orcamento, Service_catalog
from service.services.viacep import EnderecoViaCep


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
        self.assertContains(response, "Orcar item")

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

    def test_cria_lead_com_endereco_via_cep(self):
        response = self.client.post(
            reverse("novo_lead"),
            {
                "name": "Lead CEP",
                "email": "lead-cep@teste.com",
                "telefone": "11933334444",
                "cep": "01001-000",
                "logradouro": "Praca da Se",
                "numero": "200",
                "complemento": "Casa",
                "bairro": "Se",
                "cidade": "Sao Paulo",
                "uf": "sp",
                "status": Cliente.Status.NOVO,
            },
        )

        self.assertEqual(response.status_code, 302)
        cliente = Cliente.objects.get(email="lead-cep@teste.com")
        self.assertEqual(cliente.cep, "01001-000")
        self.assertEqual(cliente.logradouro, "Praca da Se")
        self.assertEqual(cliente.numero, "200")
        self.assertEqual(cliente.bairro, "Se")
        self.assertEqual(cliente.cidade, "Sao Paulo")
        self.assertEqual(cliente.uf, "SP")
        self.assertIn("Praca da Se, 200", cliente.endereco)

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
        categoria = CategoriaCatalogo.objects.create(name="Sofas")
        response = self.client.post(
            reverse("novo_produto"),
            {
                "name": "Sofa retratil 3 lugares",
                "categoria": categoria.pk,
                "valor": 59.9,
                "descricao": "Higienizacao completa de sofa.",
                "tempo": "2 horas",
                "formato": "Retratil",
                "tamanho": "Grande",
                "largura": "70 cm",
                "comprimento": "300 cm",
                "tecido": "Suede",
            },
        )

        self.assertEqual(response.status_code, 302)
        produto = Service_catalog.objects.get(name="Sofa retratil 3 lugares")
        self.assertEqual(produto.categoria, categoria)
        self.assertEqual(produto.tipo, "Sofas")

    def test_cria_categoria_do_catalogo(self):
        response = self.client.post(
            reverse("nova_categoria"),
            {
                "name": "Tapetes",
                "descricao": "Itens de higienizacao para tapetes.",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(CategoriaCatalogo.objects.filter(name="Tapetes").exists())

    def test_edita_item_do_catalogo(self):
        categoria = CategoriaCatalogo.objects.create(name="Colchoes")

        response = self.client.post(
            reverse("editar_produto", args=[self.item_a.pk]),
            {
                "name": "Colchao queen",
                "categoria": categoria.pk,
                "valor": 180.0,
                "descricao": "Higienizacao de colchao queen.",
                "tempo": "2 horas",
                "formato": "Queen",
                "tamanho": "Queen",
                "largura": "158 cm",
                "comprimento": "198 cm",
                "tecido": "Malha",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.item_a.refresh_from_db()
        self.assertEqual(self.item_a.name, "Colchao queen")
        self.assertEqual(self.item_a.categoria, categoria)
        self.assertEqual(self.item_a.tipo, "Colchoes")

    def test_deleta_item_do_catalogo(self):
        response = self.client.post(reverse("deletar_produto", args=[self.item_b.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Service_catalog.objects.filter(pk=self.item_b.pk).exists())

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

    def test_cria_orcamento_com_endereco_via_cep(self):
        response = self.client.post(
            reverse("novo_orcamento"),
            {
                "name": "Cliente CEP",
                "email": "cep@teste.com",
                "telefone": "11999999999",
                "cep": "01001-000",
                "logradouro": "Praca da Se",
                "numero": "100",
                "complemento": "Sala 2",
                "bairro": "Se",
                "cidade": "Sao Paulo",
                "uf": "sp",
                "descricao": "Pedido com endereco estruturado",
                "quantidade": 1,
                "itens": [self.item_a.pk],
            },
        )

        self.assertEqual(response.status_code, 302)
        orcamento = Orcamento.objects.get(name="Cliente CEP")
        self.assertEqual(orcamento.cep, "01001-000")
        self.assertEqual(orcamento.logradouro, "Praca da Se")
        self.assertEqual(orcamento.numero, "100")
        self.assertEqual(orcamento.bairro, "Se")
        self.assertEqual(orcamento.cidade, "Sao Paulo")
        self.assertEqual(orcamento.uf, "SP")
        self.assertIn("Praca da Se, 100", orcamento.endereco)

    @patch("service.views.orcamentos.ViaCepService")
    def test_busca_endereco_por_cep(self, service_mock):
        service_mock.return_value.buscar_por_cep.return_value = EnderecoViaCep(
            cep="01001-000",
            logradouro="Praca da Se",
            bairro="Se",
            cidade="Sao Paulo",
            uf="SP",
            complemento="lado impar",
        )

        response = self.client.get(reverse("buscar_endereco_cep", args=["01001000"]))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["endereco"]["logradouro"], "Praca da Se")
        self.assertEqual(payload["endereco"]["cidade"], "Sao Paulo")

    def test_novo_orcamento_preseleciona_item_do_catalogo(self):
        response = self.client.get(f"{reverse('novo_orcamento')}?item={self.item_a.pk}")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.item_a.name)
        self.assertContains(response, f'value="{self.item_a.pk}" selected')

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
