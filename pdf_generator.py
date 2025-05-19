import io
from fpdf import FPDF

# Função apenas para gerar PDF a partir de texto limpo sem Markdown/asteriscos
def gerar_pdf(nome: str, texto: str) -> bytes:
    """
    Gera um PDF estilizado:
    - Título centralizado
    - Nome do usuário
    - Dias da semana em destaque
    - Listagem numerada
    - Dicas como bullets em itálico
    - Rodapé com crédito
    - Não use asteriscos
    """
    # Limpa Markdown e asteriscos



    lines = [line.strip() for line in texto_limpo.splitlines()]

    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()

    # Cabeçalho
    pdf.set_font('Arial', 'B', 18)
    pdf.set_text_color(30, 144, 255)
    pdf.cell(0, 12, 'Plano de Treino Personalizado de Jack', ln=True, align='C')
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
        # Dia da semana (contém '–' e não começa com número)
        if '–' in txt and not txt[0].isdigit():
            pdf.set_font('Arial', 'B', 13)
            pdf.set_text_color(46, 134, 222)
            pdf.cell(0, 8, txt, ln=True)
            pdf.ln(1)
        # Itens numerados
        elif txt[0].isdigit():
            pdf.set_font('Arial', '', 11)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(5)
            pdf.multi_cell(0, 6, txt)
        # Dicas personalizadas (bullets)
        elif txt.startswith('-'):
            pdf.set_font('Arial', 'I', 10)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(10)
            pdf.multi_cell(0, 5, f'• {txt[1:].strip()}')
        # Orientações gerais e outros
        else:
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
