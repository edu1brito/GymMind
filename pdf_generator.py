import io
import re
from fpdf import FPDF

def quebra_palavras_longa(texto, limite=40):
    """
    Quebra palavras muito longas para evitar erro de renderização no FPDF.
    """
    return re.sub(
        r'\S{' + str(limite) + r',}',
        lambda m: ' '.join([m.group(0)[i:i+limite] for i in range(0, len(m.group(0)), limite)]),
        texto
    )

# Função para gerar PDF a partir de texto limpo
def gerar_pdf(nome: str, texto: str) -> bytes:
    """
    Gera um PDF estilizado:
    - Título centralizado
    - Nome do usuário
    - Dias da semana em destaque
    - Listagem numerada
    - Dicas como bullets em itálico
    - Rodapé com crédito
    """
    # Limpeza e proteção contra erros do PDF
    texto_limpo = texto.replace('*', '').replace('–', '-').replace('—', '-').replace('•', '-')
    texto_limpo = quebra_palavras_longa(texto_limpo)
    lines = [line.strip() for line in texto_limpo.splitlines()]

    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()

    # Cabeçalho
    pdf.set_font('Arial', 'B', 18)
    pdf.set_text_color(30, 144, 255)
    pdf.cell(0, 12, 'Plano de Treino Personalizado', ln=True, align='C')
    pdf.ln(4)

    # Nome do usuário
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, f'Nome: {nome}', ln=True)
    pdf.ln(6)

    # Corpo do plano
    for txt in lines:
        if not txt:
            pdf.ln(2)
            continue
        if '-' in txt and not txt[0].isdigit():
            # Dia da semana
            pdf.set_font('Arial', 'B', 13)
            pdf.set_text_color(46, 134, 222)
            pdf.cell(0, 8, txt, ln=True)
            pdf.ln(1)
        elif txt[0].isdigit():
            # Exercício numerado
            pdf.set_font('Arial', '', 11)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(5)
            pdf.multi_cell(0, 6, txt)
        elif txt.startswith('-'):
            # Dica personalizada
            pdf.set_font('Arial', 'I', 10)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(10)
            pdf.multi_cell(0, 5, f'- {txt[1:].strip()}')
        else:
            # Orientações gerais
            pdf.set_font('Arial', 'I', 10)
            pdf.set_text_color(80, 80, 80)
            pdf.multi_cell(0, 5, txt)

    # Rodapé
    pdf.set_y(-20)
    pdf.set_font('Arial', 'I', 9)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 5, 'Gerado por GymMind IA', align='C')

    buffer = io.BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()
