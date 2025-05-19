import io
import re
from fpdf import FPDF

def quebra_palavras_longa(texto: str, limite=30) -> str:
    """
    Insere espaços artificiais em palavras muito longas para evitar erros no FPDF.
    """
    return re.sub(
        rf'(\S{{{limite},}})',
        lambda m: ' '.join(m.group(0)[i:i+limite] for i in range(0, len(m.group(0)), limite)),
        texto
    )

def limpar_texto(texto: str) -> str:
    """
    Remove símbolos problemáticos e aplica quebra de palavras longas.
    """
    texto = texto.replace('•', '-')
    texto = texto.replace('*', '')
    texto = texto.replace('–', '-').replace('—', '-')
    texto = quebra_palavras_longa(texto)
    return texto

def gerar_pdf(nome: str, texto: str) -> bytes:
    texto_limpo = limpar_texto(texto)
    linhas = [linha.strip() for linha in texto_limpo.splitlines()]

    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()

    # Cabeçalho
    pdf.set_font('Arial', 'B', 18)
    pdf.set_text_color(30, 144, 255)
    pdf.cell(0, 12, 'Plano de Treino Personalizado', ln=True, align='C')
    pdf.ln(4)

    # Nome
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, f'Nome: {nome}', ln=True)
    pdf.ln(6)

    # Corpo
    for linha in linhas:
        if not linha:
            pdf.ln(2)
            continue

        if '-' in linha and not linha[0].isdigit():
            # Dia da semana
            pdf.set_font('Arial', 'B', 13)
            pdf.set_text_color(46, 134, 222)
            pdf.cell(0, 8, linha, ln=True)
            pdf.ln(1)
        elif linha[0].isdigit():
            # Exercício
            pdf.set_font('Arial', '', 11)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(5)
            pdf.multi_cell(0, 6, linha)
        elif linha.startswith('-'):
            # Dica
            pdf.set_font('Arial', 'I', 10)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(10)
            pdf.multi_cell(0, 5, f'- {linha[1:].strip()}')
        else:
            # Orientações gerais
            pdf.set_font('Arial', 'I', 10)
            pdf.set_text_color(80, 80, 80)
            pdf.multi_cell(0, 5, linha)

    # Rodapé
    pdf.set_y(-20)
    pdf.set_font('Arial', 'I', 9)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 5, 'Gerado por GymMind IA', align='C')

    buffer = io.BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()
