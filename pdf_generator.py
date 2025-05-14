
from fpdf import FPDF, HTMLMixin
from fpdf.html import HTML2FPDF
from html import unescape as html_unescape
from jinja2 import Environment, FileSystemLoader
import io

# Monkey-patch para corrigir o AttributeError do unescape
HTML2FPDF.unescape = staticmethod(html_unescape)

class PDF(HTMLMixin, FPDF):
    pass

def gerar_pdf(nome: str, treino: list[dict]) -> bytes:
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("treino_template.html")
    html = template.render(nome=nome, treino=treino)

    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.write_html(html)

    buffer = io.BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()