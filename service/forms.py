from django import forms

from service.models import CategoriaCatalogo, Cliente, Orcamento, Service_catalog


class CategoriaCatalogoForm(forms.ModelForm):
    class Meta:
        model = CategoriaCatalogo
        fields = ["name", "descricao"]
        labels = {
            "name": "Nome da categoria",
            "descricao": "Descricao",
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Ex.: Sofas"}),
            "descricao": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Ex.: Itens de higienizacao para sofas, poltronas e chaises."}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["descricao"].required = False
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class ProdutoCatalogoForm(forms.ModelForm):
    class Meta:
        model = Service_catalog
        fields = [
            "name",
            "categoria",
            "valor",
            "descricao",
            "tempo",
            "formato",
            "tamanho",
            "largura",
            "comprimento",
            "tecido",
        ]
        labels = {
            "name": "Nome do servico ou item",
            "categoria": "Categoria",
            "valor": "Valor base",
            "descricao": "Descricao",
            "tempo": "Tempo medio",
            "formato": "Formato",
            "tamanho": "Tamanho",
            "largura": "Largura",
            "comprimento": "Comprimento",
            "tecido": "Material ou tecido",
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Ex.: Sofa retratil 3 lugares"}),
            "categoria": forms.Select(),
            "valor": forms.NumberInput(attrs={"step": "0.01", "placeholder": "0.00"}),
            "descricao": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Ex.: Higienizacao profunda com extratora e acabamento antiodor."}
            ),
            "tempo": forms.TextInput(attrs={"placeholder": "Ex.: 2 horas"}),
            "formato": forms.TextInput(attrs={"placeholder": "Ex.: Retratil, chaise, canto"}),
            "tamanho": forms.TextInput(attrs={"placeholder": "Ex.: 2 lugares, queen, 2x3 m"}),
            "largura": forms.TextInput(attrs={"placeholder": "Ex.: 180 cm"}),
            "comprimento": forms.TextInput(attrs={"placeholder": "Ex.: 220 cm"}),
            "tecido": forms.TextInput(attrs={"placeholder": "Ex.: Suede, linho, veludo"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in [
            "categoria",
            "descricao",
            "tempo",
            "formato",
            "tamanho",
            "largura",
            "comprimento",
            "tecido",
        ]:
            self.fields[field_name].required = False

        for name, field in self.fields.items():
            widget = field.widget
            current_class = widget.attrs.get("class", "")
            base_class = "form-control"
            if name == "categoria":
                base_class = "form-select"
            widget.attrs["class"] = f"{current_class} {base_class}".strip()

    def save(self, commit=True):
        item = super().save(commit=False)
        item.tipo = item.categoria.name if item.categoria else None
        if commit:
            item.save()
            self.save_m2m()
        return item


class ClienteForm(forms.ModelForm):
    orcamento_origem = forms.ModelChoiceField(
        label="Puxar dados de um orcamento",
        queryset=Orcamento.objects.none(),
        required=False,
        empty_label="Preencher manualmente ou selecionar orcamento",
        widget=forms.Select(),
    )

    class Meta:
        model = Cliente
        fields = [
            "name",
            "email",
            "telefone",
            "cep",
            "logradouro",
            "numero",
            "complemento",
            "bairro",
            "cidade",
            "uf",
            "endereco",
            "status",
        ]
        labels = {
            "name": "Nome do cliente",
            "email": "Email",
            "telefone": "Telefone",
            "cep": "CEP",
            "logradouro": "Logradouro",
            "numero": "Numero",
            "complemento": "Complemento",
            "bairro": "Bairro",
            "cidade": "Cidade",
            "uf": "UF",
            "status": "Status",
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Ex.: Maria Souza"}),
            "email": forms.EmailInput(attrs={"placeholder": "cliente@empresa.com"}),
            "telefone": forms.TextInput(attrs={"placeholder": "(11) 99999-9999"}),
            "cep": forms.TextInput(attrs={"placeholder": "00000-000", "autocomplete": "postal-code"}),
            "logradouro": forms.TextInput(attrs={"placeholder": "Rua, avenida ou travessa"}),
            "numero": forms.TextInput(attrs={"placeholder": "Numero"}),
            "complemento": forms.TextInput(attrs={"placeholder": "Apartamento, bloco, referencia"}),
            "bairro": forms.TextInput(attrs={"placeholder": "Bairro"}),
            "cidade": forms.TextInput(attrs={"placeholder": "Cidade"}),
            "uf": forms.TextInput(attrs={"placeholder": "SP"}),
            "endereco": forms.HiddenInput(),
            "status": forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        if args and args[0] is not None:
            args = (self._data_com_orcamento(args[0]), *args[1:])
        elif kwargs.get("data") is not None:
            kwargs["data"] = self._data_com_orcamento(kwargs["data"])

        super().__init__(*args, **kwargs)
        self.fields["orcamento_origem"].queryset = Orcamento.objects.filter(cliente__isnull=True).order_by(
            "-created_at", "-id"
        )
        self.fields["orcamento_origem"].label_from_instance = self._orcamento_label
        self.fields["orcamento_origem"].widget.attrs["class"] = "form-select"
        for field_name in [
            "telefone",
            "cep",
            "logradouro",
            "numero",
            "complemento",
            "bairro",
            "cidade",
            "uf",
            "endereco",
        ]:
            self.fields[field_name].required = False

        for name, field in self.fields.items():
            if name == "status":
                field.widget.attrs["class"] = "form-select"
            elif name != "endereco":
                field.widget.attrs["class"] = "form-control text-uppercase" if name == "uf" else "form-control"

    @staticmethod
    def _orcamento_label(orcamento: Orcamento) -> str:
        contato = orcamento.email or orcamento.telefone or "sem contato"
        return f"#{orcamento.pk} - {orcamento.name} ({contato})"

    @staticmethod
    def _data_com_orcamento(data):
        mutable_data = data.copy()
        orcamento_id = mutable_data.get("orcamento_origem")
        if not orcamento_id:
            return mutable_data

        orcamento = Orcamento.objects.filter(pk=orcamento_id, cliente__isnull=True).first()
        if not orcamento:
            return mutable_data

        for field_name in [
            "name",
            "email",
            "telefone",
            "cep",
            "logradouro",
            "numero",
            "complemento",
            "bairro",
            "cidade",
            "uf",
            "endereco",
        ]:
            if not mutable_data.get(field_name):
                mutable_data[field_name] = getattr(orcamento, field_name, None) or ""

        if not mutable_data.get("status"):
            mutable_data["status"] = Cliente.Status.CONVERTIDO

        return mutable_data

    def clean(self):
        cleaned_data = super().clean()
        endereco = montar_endereco_limpo(cleaned_data)
        cleaned_data["uf"] = (cleaned_data.get("uf") or "").strip().upper()
        cleaned_data["endereco"] = endereco or (cleaned_data.get("endereco") or "").strip()
        return cleaned_data


class OrcamentoForm(forms.Form):
    cliente = forms.ModelChoiceField(
        label="Cliente ja cadastrado",
        queryset=Cliente.objects.none(),
        required=False,
        empty_label="Preencher manualmente ou selecionar cliente",
        widget=forms.Select(),
    )
    criar_cliente_automatico = forms.BooleanField(
        label="Criar cliente automaticamente ao salvar",
        required=False,
    )
    name = forms.CharField(
        label="Nome do cliente",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Ex.: Maria Souza"}),
    )
    email = forms.EmailField(
        label="Email",
        required=False,
        widget=forms.EmailInput(attrs={"placeholder": "cliente@empresa.com"}),
    )
    telefone = forms.CharField(
        label="Telefone",
        required=False,
        max_length=20,
        widget=forms.TextInput(attrs={"placeholder": "(11) 99999-9999"}),
    )
    cep = forms.CharField(
        label="CEP",
        required=False,
        max_length=9,
        widget=forms.TextInput(attrs={"placeholder": "00000-000", "autocomplete": "postal-code"}),
    )
    logradouro = forms.CharField(
        label="Logradouro",
        required=False,
        max_length=120,
        widget=forms.TextInput(attrs={"placeholder": "Rua, avenida ou travessa"}),
    )
    numero = forms.CharField(
        label="Numero",
        required=False,
        max_length=20,
        widget=forms.TextInput(attrs={"placeholder": "Numero"}),
    )
    complemento = forms.CharField(
        label="Complemento",
        required=False,
        max_length=120,
        widget=forms.TextInput(attrs={"placeholder": "Apartamento, bloco, referencia"}),
    )
    bairro = forms.CharField(
        label="Bairro",
        required=False,
        max_length=120,
        widget=forms.TextInput(attrs={"placeholder": "Bairro"}),
    )
    cidade = forms.CharField(
        label="Cidade",
        required=False,
        max_length=120,
        widget=forms.TextInput(attrs={"placeholder": "Cidade"}),
    )
    uf = forms.CharField(
        label="UF",
        required=False,
        max_length=2,
        widget=forms.TextInput(attrs={"placeholder": "SP"}),
    )
    endereco = forms.CharField(required=False, widget=forms.HiddenInput())
    descricao = forms.CharField(
        label="Observacoes",
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "placeholder": "Detalhes do pedido, prazo ou acabamento.",
            }
        ),
    )
    quantidade = forms.IntegerField(
        label="Quantidade",
        min_value=1,
        initial=1,
    )
    itens = forms.ModelMultipleChoiceField(
        label="Itens do catalogo",
        queryset=Service_catalog.objects.none(),
        widget=forms.SelectMultiple(attrs={"size": 8}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["cliente"].queryset = Cliente.objects.order_by("name", "email")
        self.fields["itens"].queryset = Service_catalog.objects.select_related("categoria").order_by("categoria__name", "tipo", "name")
        self.fields["itens"].label_from_instance = self._catalogo_item_label
        self.fields["cliente"].widget.attrs["class"] = "form-select"
        self.fields["criar_cliente_automatico"].widget.attrs["class"] = "form-check-input"
        self.fields["name"].widget.attrs["class"] = "form-control"
        self.fields["email"].widget.attrs["class"] = "form-control"
        self.fields["telefone"].widget.attrs["class"] = "form-control"
        self.fields["cep"].widget.attrs["class"] = "form-control"
        self.fields["logradouro"].widget.attrs["class"] = "form-control"
        self.fields["numero"].widget.attrs["class"] = "form-control"
        self.fields["complemento"].widget.attrs["class"] = "form-control"
        self.fields["bairro"].widget.attrs["class"] = "form-control"
        self.fields["cidade"].widget.attrs["class"] = "form-control"
        self.fields["uf"].widget.attrs["class"] = "form-control text-uppercase"
        self.fields["descricao"].widget.attrs["class"] = "form-control"
        self.fields["quantidade"].widget.attrs["class"] = "form-control"
        self.fields["itens"].widget.attrs["class"] = "form-select"

    @staticmethod
    def _catalogo_item_label(item: Service_catalog) -> str:
        categoria_nome = item.categoria_nome
        categoria = f"{categoria_nome} - " if categoria_nome else ""
        return f"{categoria}{item.name} | R$ {item.valor:.2f}"

    def clean(self):
        cleaned_data = super().clean()
        cliente = cleaned_data.get("cliente")
        if cliente:
            for field_name in [
                "name",
                "email",
                "telefone",
                "cep",
                "logradouro",
                "numero",
                "complemento",
                "bairro",
                "cidade",
                "uf",
                "endereco",
            ]:
                if not cleaned_data.get(field_name):
                    cleaned_data[field_name] = getattr(cliente, field_name, None) or ""
            cleaned_data["criar_cliente_automatico"] = False

        cleaned_data["uf"] = (cleaned_data.get("uf") or "").strip().upper()
        cleaned_data["endereco"] = montar_endereco_limpo(cleaned_data) or (cleaned_data.get("endereco") or "").strip()
        if not cleaned_data.get("cliente") and not cleaned_data.get("name"):
            self.add_error("name", "Informe o nome do cliente ou selecione um cliente cadastrado.")
        if cleaned_data.get("criar_cliente_automatico") and not cleaned_data.get("email"):
            self.add_error("email", "Informe um email para criar o cliente automaticamente.")
        return cleaned_data


class ClienteVinculoOrcamentoForm(forms.Form):
    cliente = forms.ModelChoiceField(
        label="Cliente cadastrado",
        queryset=Cliente.objects.none(),
        empty_label="Selecione um cliente",
        widget=forms.Select(),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["cliente"].queryset = Cliente.objects.order_by("name", "email")
        self.fields["cliente"].widget.attrs["class"] = "form-select"


def montar_endereco_limpo(cleaned_data: dict) -> str:
    logradouro = (cleaned_data.get("logradouro") or "").strip()
    numero = (cleaned_data.get("numero") or "").strip()
    complemento = (cleaned_data.get("complemento") or "").strip()
    bairro = (cleaned_data.get("bairro") or "").strip()
    cidade = (cleaned_data.get("cidade") or "").strip()
    uf = (cleaned_data.get("uf") or "").strip().upper()

    partes = []
    if logradouro:
        partes.append(f"{logradouro}, {numero}" if numero else logradouro)
    if complemento:
        partes.append(complemento)
    if bairro:
        partes.append(bairro)
    cidade_uf = " - ".join(parte for parte in [cidade, uf] if parte)
    if cidade_uf:
        partes.append(cidade_uf)

    return " | ".join(partes)
