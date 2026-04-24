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

    def test_aprova_orcamento_e_cria_cliente(self):
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
