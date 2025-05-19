import io
import re
from fpdf import FPDF

def quebra_palavras_longa(texto: str, limite=20) -> str:
    # Usa zero-width spaces para quebras invisíveis mais seguras
    return re.sub(
        rf'(\S{{{limite},}})',
        lambda m: '\u200b'.join(
            m.group(0)[i:i+limite]
            for i in range(0, len(m.group(0)), limite)
        ),
        texto
    )

def limpar_texto(texto: str) -> str:
    simbolos = {'•':'-', '*':'', '–':'-', '—':'-',
                '”':'"', '“':'"', '’':"'", '‘':"'"}
    for s, sub in simbolos.items():
        texto = texto.replace(s, sub)
    return quebra_palavras_longa(texto)

def gerar_pdf(nome: str, texto: str) -> bytes:
    texto_limpo = limpar_texto(texto)
    linhas = [l.strip() for l in texto_limpo.splitlines()]

    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_left_margin(10)
    pdf.set_right_margin(10)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Cabeçalho
    pdf.set_font('Arial', 'B', 18)
    pdf.set_text_color(30,144,255)
    pdf.cell(0, 12, 'Plano de Treino Personalizado', ln=True, align='C')
    pdf.ln(6)

    # Nome
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(0,0,0)
    pdf.cell(0, 8, f'Nome: {nome}', ln=True)
    pdf.ln(6)

    # Corpo
    for linha in linhas:
        if not linha:
            pdf.ln(2)
            continue

        if '-' in linha and not linha[0].isdigit():
            pdf.set_font('Arial', 'B', 13)
            pdf.set_text_color(46,134,222)
            pdf.multi_cell(180, 8, linha)
            pdf.ln(1)

        elif linha[0].isdigit():
            pdf.set_font('Arial', '', 11)
            pdf.set_text_color(0,0,0)
            pdf.cell(5)
            pdf.multi_cell(180, 6, linha)

        elif linha.startswith('-'):
            pdf.set_font('Arial', 'I', 10)
            pdf.set_text_color(80,80,80)
            pdf.cell(10)
            pdf.multi_cell(170, 5, f'- {linha[1:].strip()}')

        else:
            pdf.set_font('Arial', 'I', 10)
            pdf.set_text_color(80,80,80)
            pdf.multi_cell(180, 5, linha)

    # Rodapé
    pdf.set_y(-20)
    pdf.set_font('Arial', 'I', 9)
    pdf.set_text_color(150,150,150)
    pdf.cell(0, 5, 'Gerado por GymMind IA', align='C')

    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer.getvalue()
