import io
import re
from fpdf import FPDF

def quebra_palavras_longa(texto: str, limite=30) -> str:
    """
    Insere espaços artificiais em palavras muito longas para evitar estouro de linha no FPDF.
    """
    return re.sub(
        rf'(\S{{{limite},}})',
        lambda m: ' '.join(m.group(0)[i:i+limite] for i in range(0, len(m.group(0)), limite)),
        texto
    )

def limpar_texto(texto: str) -> str:
    """
    Substitui caracteres problemáticos e quebra palavras muito longas.
    """
    simbolos_problematicos = {
        '•': '-', '*': '',
        '–': '-', '—': '-',  # travessões diferentes
        '”': '"', '“': '"', '’': "'", '‘': "'"
    }
    for simbolo, substituto in simbolos_problematicos.items():
        texto = texto.replace(simbolo, substituto)
    return quebra_palavras_longa(texto)

def gerar_pdf(nome: str, texto: str) -> bytes:
    """
    Gera um PDF personalizado com o plano de treino.
    """
    texto_limpo = limpar_texto(texto)
    linhas = [linha.strip() for linha in texto_limpo.splitlines()]

    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()

    # Cabeçalho
    pdf.set_font('Arial', 'B', 18)
    pdf.set_text_color(30, 144, 255)
    pdf.cell(0, 12, 'Plano de Treino Personalizado', ln=True, align='C')
    pdf.ln(6)

    # Nome do usuário
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, f'Nome: {nome}', ln=True)
    pdf.ln(6)

    # Corpo do plano
    for linha in linhas:
        if not linha:
            pdf.ln(2)
            continue

        if '-' in linha and not linha[0].isdigit():
            # Cabeçalho do dia (ex: Segunda - Peito e Tríceps)
            pdf.set_font('Arial', 'B', 13)
            pdf.set_text_color(46, 134, 222)
            pdf.multi_cell(0, 8, linha)
            pdf.ln(1)

        elif linha[0].isdigit():
            # Exercícios numerados
            pdf.set_font('Arial', '', 11)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(5)
            pdf.multi_cell(0, 6, linha)

        elif linha.startswith('-'):
            # Dicas (começam com "-")
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
    buffer.seek(0)
    return buffer.getvalue()
