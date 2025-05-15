from fpdf import FPDF, HTMLMixin
from fpdf.html import HTML2FPDF
from html import unescape as html_unescape
import io

# Corrige erro de unescape para HTML
HTML2FPDF.unescape = staticmethod(html_unescape)

class PDF(FPDF, HTMLMixin):
    pass

def gerar_pdf(nome: str, treino: list[dict]) -> bytes:
    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    # Título
    pdf.set_text_color(46, 134, 222)
    pdf.set_font_size(18)
    pdf.cell(0, 10, f"Plano de Treino de {nome}", ln=True, align="C")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)

    for dia in treino:
        pdf.set_font_size(14)
        pdf.set_text_color(44, 62, 80)
        pdf.cell(0, 10, dia["dia"], ln=True)
        pdf.set_text_color(0, 0, 0)

        pdf.set_font_size(12)
        pdf.set_fill_color(223, 240, 255)
        pdf.cell(90, 8, "Exercício", 1, 0, 'C', fill=True)
        pdf.cell(30, 8, "Séries", 1, 0, 'C', fill=True)
        pdf.cell(30, 8, "Repetições", 1, 1, 'C', fill=True)

        for ex in dia["exercicios"]:
            pdf.cell(90, 8, ex["nome"], 1)
            pdf.cell(30, 8, str(ex["series"]), 1)
            pdf.cell(30, 8, str(ex["repeticoes"]), 1)
            pdf.ln()

        pdf.ln(5)

    buffer = io.BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()
