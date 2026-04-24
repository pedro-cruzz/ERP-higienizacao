from django import forms

from service.models import Service_catalog


class ProdutoCatalogoForm(forms.ModelForm):
    class Meta:
        model = Service_catalog
        fields = [
            "name",
            "tipo",
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
            "name": "Nome do produto",
            "tipo": "Tipo",
            "valor": "Valor base",
            "descricao": "Descricao",
            "tempo": "Tempo de producao",
            "formato": "Formato",
            "tamanho": "Tamanho",
            "largura": "Largura",
            "comprimento": "Comprimento",
            "tecido": "Tecido",
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Ex.: Banner promocional"}),
            "tipo": forms.TextInput(attrs={"placeholder": "Ex.: Impressao"}),
            "valor": forms.NumberInput(attrs={"step": "0.01", "placeholder": "0.00"}),
            "descricao": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Detalhes do produto e acabamento."}
            ),
            "tempo": forms.TextInput(attrs={"placeholder": "Ex.: 2 dias uteis"}),
            "formato": forms.TextInput(attrs={"placeholder": "Ex.: 1x1 m"}),
            "tamanho": forms.TextInput(attrs={"placeholder": "Ex.: Medio"}),
            "largura": forms.TextInput(attrs={"placeholder": "Ex.: 100 cm"}),
            "comprimento": forms.TextInput(attrs={"placeholder": "Ex.: 100 cm"}),
            "tecido": forms.TextInput(attrs={"placeholder": "Ex.: Lona front"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in [
            "tipo",
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
            if name == "valor":
                base_class = "form-control"
            widget.attrs["class"] = f"{current_class} {base_class}".strip()


class OrcamentoForm(forms.Form):
    name = forms.CharField(
        label="Nome do cliente",
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Ex.: Maria Souza"}),
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "cliente@empresa.com"}),
    )
    telefone = forms.CharField(
        label="Telefone",
        required=False,
        max_length=20,
        widget=forms.TextInput(attrs={"placeholder": "(11) 99999-9999"}),
    )
    endereco = forms.CharField(
        label="Endereco",
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={"placeholder": "Rua, numero, bairro"}),
    )
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
        self.fields["itens"].queryset = Service_catalog.objects.all()
        self.fields["name"].widget.attrs["class"] = "form-control"
        self.fields["email"].widget.attrs["class"] = "form-control"
        self.fields["telefone"].widget.attrs["class"] = "form-control"
        self.fields["endereco"].widget.attrs["class"] = "form-control"
        self.fields["descricao"].widget.attrs["class"] = "form-control"
        self.fields["quantidade"].widget.attrs["class"] = "form-control"
        self.fields["itens"].widget.attrs["class"] = "form-select"
