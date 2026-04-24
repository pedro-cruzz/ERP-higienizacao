import textwrap
from io import BytesIO

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from service.forms import OrcamentoForm
from service.models import Cliente, Orcamento


def novo_orcamento(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = OrcamentoForm(request.POST)
        if form.is_valid():
            itens = list(form.cleaned_data["itens"])
            quantidade = form.cleaned_data["quantidade"]
            valor_total = sum(item.valor for item in itens) * quantidade

            orcamento = Orcamento.objects.create(
                name=form.cleaned_data["name"],
                email=form.cleaned_data["email"],
                telefone=form.cleaned_data["telefone"] or None,
                endereco=form.cleaned_data["endereco"] or None,
                descricao=form.cleaned_data["descricao"] or None,
                quantidade=quantidade,
                valor=valor_total,
            )
            orcamento.itens.set(itens)

            messages.success(request, "Orcamento criado com sucesso.")
            return redirect("orcamento_detalhe", pk=orcamento.pk)
    else:
        form = OrcamentoForm()

    context = {
        "form": form,
        "orcamentos_recentes": Orcamento.objects.prefetch_related("itens").order_by("-id")[:5],
    }
    return render(request, "service/orcamento_form.html", context)


def detalhe_orcamento(request: HttpRequest, pk: int) -> HttpResponse:
    orcamento = get_object_or_404(
        Orcamento.objects.prefetch_related("itens", "cliente"),
        pk=pk,
    )
    context = {
        "orcamento": orcamento,
        "itens": orcamento.itens.all(),
    }
    return render(request, "service/orcamento_detalhe.html", context)


def aprovar_orcamento(request: HttpRequest, pk: int) -> HttpResponse:
    if request.method != "POST":
        return redirect("orcamento_detalhe", pk=pk)

    orcamento = get_object_or_404(Orcamento, pk=pk)

    if not orcamento.email:
        messages.error(
            request,
            "Este orcamento precisa de um email para criar o cadastro do cliente.",
        )
        return redirect("orcamento_detalhe", pk=pk)

    cliente = Cliente.objects.filter(email=orcamento.email).first()
    if cliente is None:
        cliente = Cliente.objects.create(
            name=orcamento.name,
            email=orcamento.email,
            telefone=orcamento.telefone,
            endereco=orcamento.endereco,
        )
    else:
        cliente.name = orcamento.name
        cliente.telefone = orcamento.telefone
        cliente.endereco = orcamento.endereco
        cliente.save()

    orcamento.cliente = cliente
    orcamento.aprovado = True
    orcamento.save(update_fields=["cliente", "aprovado"])

    messages.success(
        request,
        "Orcamento aprovado e cliente vinculado com sucesso.",
    )
    return redirect("orcamento_detalhe", pk=pk)


def gerar_orcamento_pdf(request: HttpRequest, pk: int) -> HttpResponse:
    orcamento = get_object_or_404(
        Orcamento.objects.prefetch_related("itens", "cliente"),
        pk=pk,
    )
    itens = list(orcamento.itens.all())

    page_width, page_height = A4
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setTitle(f"Orcamento {orcamento.pk}")

    navy = colors.HexColor("#1D2C3C")
    ink = colors.HexColor("#263748")
    blue = colors.HexColor("#3B97D3")
    blue_dark = colors.HexColor("#2577B5")
    aqua = colors.HexColor("#76C7D9")
    blue_pale = colors.HexColor("#EEF7FD")
    blue_glow = colors.HexColor("#DCECF8")
    card = colors.white
    line = colors.HexColor("#D7E6F1")
    shadow = colors.HexColor("#EAF1F7")
    muted = colors.HexColor("#6C7B8B")
    soft_text = colors.HexColor("#8292A3")

    main_x = 40
    main_y = 34
    main_w = 515
    main_h = 772

    def money(value: float) -> str:
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def wrap_lines(value: str, width: int, max_lines: int = 2) -> list[str]:
        lines = textwrap.wrap(value or "-", width=width) or ["-"]
        return lines[:max_lines]

    def item_detail_lines(item) -> list[str]:
        material = (
            f"Tecido: {item.tecido}"
            if item.tecido
            else f"Tipo: {item.tipo}"
            if item.tipo
            else "Servico: Higienizacao profissional"
        )
        complemento = (
            item.descricao
            or item.formato
            or item.tamanho
            or item.tempo
            or "Limpeza profunda com acabamento tecnico"
        )
        return [
            wrap_lines(material, 44, 1)[0],
            wrap_lines(f"Detalhe: {complemento}", 44, 1)[0],
        ]

    def draw_card(x: float, y: float, width: float, height: float, radius: float = 18) -> None:
        pdf.setFillColor(shadow)
        pdf.roundRect(x + 8, y - 8, width, height, radius, stroke=0, fill=1)
        pdf.setFillColor(card)
        pdf.setStrokeColor(line)
        pdf.setLineWidth(1)
        pdf.roundRect(x, y, width, height, radius, stroke=1, fill=1)

    def draw_main_shell() -> None:
        pdf.setFillColor(colors.white)
        pdf.rect(0, 0, page_width, page_height, stroke=0, fill=1)
        pdf.setFillColor(blue_pale)
        pdf.circle(78, 764, 54, stroke=0, fill=1)
        pdf.circle(530, 778, 92, stroke=0, fill=1)
        pdf.setFillColor(blue_glow)
        pdf.circle(545, 655, 78, stroke=0, fill=1)
        pdf.circle(50, 90, 72, stroke=0, fill=1)
        draw_card(main_x, main_y, main_w, main_h, 20)

    def draw_brand_block() -> None:
        header_x = main_x + 28
        header_y = 662
        header_w = main_w - 56
        header_h = 104
        pdf.setFillColor(navy)
        pdf.roundRect(header_x, header_y, header_w, header_h, 20, stroke=0, fill=1)
        pdf.setFillColor(colors.HexColor("#27465C"))
        pdf.roundRect(header_x, header_y + 50, header_w, 54, 20, stroke=0, fill=1)

        icon_x = header_x + 24
        icon_y = header_y + 24
        pdf.setFillColor(colors.white)
        pdf.circle(icon_x + 16, icon_y + 18, 16, stroke=0, fill=1)
        pdf.setStrokeColor(blue)
        pdf.setLineWidth(4)
        pdf.line(icon_x + 6, icon_y + 20, icon_x + 18, icon_y + 46)
        pdf.line(icon_x + 18, icon_y + 46, icon_x + 34, icon_y + 26)
        pdf.setStrokeColor(aqua)
        pdf.line(icon_x + 8, icon_y + 18, icon_x + 18, icon_y + 8)
        pdf.line(icon_x + 18, icon_y + 8, icon_x + 30, icon_y + 22)

        pdf.setFillColor(colors.white)
        pdf.setFont("Helvetica-Bold", 24)
        pdf.drawString(header_x + 74, header_y + 58, "ERP")
        pdf.setFillColor(aqua)
        pdf.drawString(header_x + 122, header_y + 58, "Higienizacao")
        pdf.setFillColor(colors.HexColor("#D4E8F7"))
        pdf.setFont("Helvetica", 11)
        pdf.drawString(header_x + 76, header_y + 38, "proposta comercial de servicos")

        meta_x = header_x + header_w - 174
        meta_y = header_y + 18
        meta_w = 148
        meta_h = 68
        pdf.setFillColor(colors.white)
        pdf.roundRect(meta_x, meta_y, meta_w, meta_h, 16, stroke=0, fill=1)
        pdf.setFillColor(soft_text)
        pdf.setFont("Helvetica", 9)
        pdf.drawString(meta_x + 16, meta_y + 48, "DOCUMENTO")
        pdf.drawString(meta_x + 16, meta_y + 26, "EMISSAO")
        pdf.setFillColor(ink)
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(meta_x + 16, meta_y + 36, f"PF-{timezone.localdate().year}-{orcamento.pk:04d}")
        pdf.drawString(meta_x + 16, meta_y + 14, timezone.localdate().strftime("%d/%m/%Y"))

    def draw_client_and_summary() -> None:
        client_x = main_x + 28
        client_y = 494
        client_w = 320
        client_h = 140
        summary_x = client_x + client_w + 16
        summary_y = client_y
        summary_w = 123
        summary_h = client_h

        draw_card(client_x, client_y, client_w, client_h, 18)
        draw_card(summary_x, summary_y, summary_w, summary_h, 18)

        pdf.setFillColor(soft_text)
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(client_x + 18, client_y + client_h - 28, "DADOS DO CLIENTE")
        pdf.setFillColor(ink)
        pdf.setFont("Helvetica-Bold", 18)
        pdf.drawString(client_x + 18, client_y + client_h - 56, (orcamento.name or "-")[:34])
        pdf.setFont("Helvetica", 11)
        pdf.drawString(client_x + 18, client_y + client_h - 82, f"Email: {(orcamento.email or '-')[:34]}")
        pdf.drawString(client_x + 18, client_y + client_h - 102, f"Telefone: {(orcamento.telefone or '-')[:28]}")
        address_lines = wrap_lines(orcamento.endereco or "Endereco nao informado", 42, 2)
        pdf.drawString(client_x + 18, client_y + client_h - 122, address_lines[0])
        if len(address_lines) > 1:
            pdf.drawString(client_x + 18, client_y + client_h - 138, address_lines[1])

        pdf.setFillColor(soft_text)
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(summary_x + 16, summary_y + summary_h - 28, "RESUMO")
        pdf.setFillColor(ink)
        pdf.setFont("Helvetica", 10)
        pdf.drawString(summary_x + 16, summary_y + summary_h - 56, "Quantidade")
        pdf.setFont("Helvetica-Bold", 18)
        pdf.drawString(summary_x + 16, summary_y + summary_h - 78, str(orcamento.quantidade))
        pdf.setFillColor(ink)
        pdf.setFont("Helvetica", 10)
        pdf.drawString(summary_x + 16, summary_y + summary_h - 102, "Calculo")
        pdf.setFillColor(muted)
        pdf.setFont("Helvetica", 8)
        pdf.drawString(summary_x + 16, summary_y + summary_h - 116, f"{len(itens)} item(ns) x {orcamento.quantidade}")
        pdf.setFillColor(ink)
        pdf.setFont("Helvetica", 10)
        pdf.drawString(summary_x + 16, summary_y + summary_h - 132, "Valor total")
        pdf.setFillColor(blue_dark)
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(summary_x + 16, summary_y + summary_h - 146, money(orcamento.valor))

    def draw_services_box(page_items: list, y: float, height: float, is_last_page: bool) -> None:
        x = main_x + 28
        w = main_w - 56
        draw_card(x, y, w, height, 20)

        pdf.setFillColor(soft_text)
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(x + 18, y + height - 28, "SERVICOS SOLICITADOS")

        header_y = y + height - 58
        pdf.setFillColor(blue_pale)
        pdf.roundRect(x + 16, header_y - 4, w - 32, 28, 10, stroke=0, fill=1)
        pdf.setFillColor(ink)
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(x + 24, header_y + 6, "SERVICO")
        pdf.drawString(x + w - 126, header_y + 6, "QTY")
        pdf.drawRightString(x + w - 24, header_y + 6, "VALOR")

        row_y = header_y - 18
        if not page_items:
            pdf.setFillColor(muted)
            pdf.setFont("Helvetica", 11)
            pdf.drawString(x + 24, row_y - 12, "Nenhum servico vinculado a este orcamento.")
        else:
            for item in page_items:
                item_box_y = row_y - 56
                pdf.setFillColor(colors.HexColor("#F9FCFE"))
                pdf.roundRect(x + 16, item_box_y, w - 32, 66, 12, stroke=0, fill=1)
                pdf.setFillColor(line)
                pdf.setLineWidth(1)
                pdf.roundRect(x + 16, item_box_y, w - 32, 66, 12, stroke=1, fill=0)

                pdf.setFillColor(ink)
                pdf.setFont("Helvetica-Bold", 13)
                pdf.drawString(x + 28, item_box_y + 44, (item.name or "-")[:38])
                info = item_detail_lines(item)
                pdf.setFillColor(muted)
                pdf.setFont("Helvetica", 9)
                pdf.drawString(x + 28, item_box_y + 27, info[0])
                pdf.drawString(x + 28, item_box_y + 12, info[1])
                pdf.setFillColor(soft_text)
                pdf.setFont("Helvetica", 8)
                pdf.drawString(
                    x + 220,
                    item_box_y + 12,
                    f"{money(item.valor)} x {orcamento.quantidade} = {money(item.valor * orcamento.quantidade)}",
                )

                pdf.setFillColor(ink)
                pdf.setFont("Helvetica-Bold", 12)
                pdf.drawCentredString(x + w - 112, item_box_y + 28, str(orcamento.quantidade))
                pdf.setFillColor(blue_dark)
                pdf.drawRightString(x + w - 28, item_box_y + 28, money(item.valor * orcamento.quantidade))

                row_y = item_box_y - 12

        if is_last_page:
            total_x = x + w - 180
            total_y = y + 20
            total_w = 156
            total_h = 74
            pdf.setFillColor(blue_pale)
            pdf.roundRect(total_x, total_y, total_w, total_h, 16, stroke=0, fill=1)
            pdf.setFillColor(blue_dark)
            pdf.setFont("Helvetica-Bold", 10)
            pdf.drawString(total_x + 16, total_y + 50, "VALOR TOTAL")
            pdf.setFont("Helvetica-Bold", 22)
            pdf.drawString(total_x + 16, total_y + 22, money(orcamento.valor))

    def draw_footer(note: str) -> None:
        footer_y = 72
        pdf.setStrokeColor(line)
        pdf.setLineWidth(1)
        pdf.line(main_x + 28, footer_y + 42, main_x + main_w - 28, footer_y + 42)
        lines = wrap_lines(note, 52, 2)
        pdf.setFillColor(muted)
        pdf.setFont("Helvetica", 10)
        pdf.drawString(main_x + 32, footer_y + 18, lines[0])
        if len(lines) > 1:
            pdf.drawString(main_x + 32, footer_y + 2, lines[1])
        draw_card(main_x + main_w - 220, footer_y - 4, 180, 54, 16)
        pdf.setFillColor(blue_dark)
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawCentredString(main_x + main_w - 130, footer_y + 16, "ORCAMENTO PRONTO")
        pdf.setFillColor(soft_text)
        pdf.setFont("Helvetica", 9)
        pdf.drawCentredString(main_x + main_w - 130, footer_y + 2, "para aprovacao e agendamento")

    emission_date = timezone.localdate().strftime("%d/%m/%Y")
    note_text = orcamento.descricao or "Valido mediante confirmacao da agenda, avaliacao tecnica e disponibilidade da equipe."

    remaining_items = itens[:]
    first_page_items = remaining_items[:4]
    remaining_items = remaining_items[4:]

    def draw_page(page_items: list, is_last_page: bool, footer_note: str) -> None:
        draw_main_shell()
        draw_brand_block()
        draw_client_and_summary()
        services_height = 272 if is_last_page else 332
        services_y = 166 if is_last_page else 146
        draw_services_box(page_items, services_y, services_height, is_last_page)
        draw_footer(footer_note)

    draw_page(first_page_items, not remaining_items, note_text)
    if remaining_items:
        pdf.showPage()

    while remaining_items:
        page_items = remaining_items[:5]
        remaining_items = remaining_items[5:]
        draw_page(
            page_items,
            not remaining_items,
            "Continuidade dos servicos detalhados neste orcamento.",
        )
        if remaining_items:
            pdf.showPage()

    pdf.save()
    pdf_bytes = buffer.getvalue()
    buffer.close()

    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="orcamento-{orcamento.pk}.pdf"'
    return response
