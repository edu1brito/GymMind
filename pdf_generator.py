import io
import re
from fpdf import FPDF

# ----------------------------------------
# Funções de limpeza do texto
# ----------------------------------------

# Regex que captura emojis, variation selectors e zero-width joiners
CLEAN_PATTERN = re.compile(
    r'('
      r'[\U00010000-\U0010FFFF]|'   # emojis e símbolos fora do BMP
      r'[\uFE00-\uFE0F]|'           # variation selectors
      r'[\u200D]'                   # zero-width joiner
    r')',
    flags=re.UNICODE
)

def remove_emojis_e_variation(texto: str) -> str:
    """
    Remove emojis, selectors de variação e zero-width joiners.
    """
    return CLEAN_PATTERN.sub('', texto)

def quebra_palavras_longa(texto: str, limite: int = 20) -> str:
    """
    Insere zero-width spaces em palavras muito longas para evitar estouro de linha.
    """
    return re.sub(
        rf'(\S{{{limite},}})',
        lambda m: '\u200b'.join(
            m.group(0)[i:i+limite]
            for i in range(0, len(m.group(0)), limite)
        ),
        texto
    )

def limpar_texto(texto: str) -> str:
    """
    Pipeline de limpeza:
     0) Elimina qualquer caractere fora do Latin‑1
     1) Remove emojis, variation selectors e zero-width joiners
     2) Substitui símbolos problemáticos por equivalentes Latin‑1
     3) Aplica quebra de palavras longas
    """
    # 0) descarta tudo que não está no Latin‑1 (0x00–0xFF)
    texto = texto.encode('latin-1', 'ignore').decode('latin-1')

    # 1) retira emojis e afins
    texto = remove_emojis_e_variation(texto)

    # 2) substitui símbolos “Unicode leve” por Latin‑1
    simbolos = {
        '•': '-', '*': '',
        '–': '-', '—': '-',
        '“': '"', '”': '"',
        '‘': "'", '’': "'"
    }
    for orig, sub in simbolos.items():
        texto = texto.replace(orig, sub)

    # 3) quebra palavras longas
    return quebra_palavras_longa(texto, limite=20)


# ----------------------------------------
# Geração do PDF
# ----------------------------------------

def gerar_pdf(nome: str, texto: str) -> bytes:
    texto_limpo = limpar_texto(texto)
    linhas = [l.strip() for l in texto_limpo.splitlines()]

    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_left_margin(10)
    pdf.set_right_margin(10)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # calcula largura útil para o corpo
    usable_width = pdf.w - pdf.l_margin - pdf.r_margin

    # Título
    pdf.set_font('Arial', 'B', 20)
    pdf.set_text_color(255, 0, 0)
    pdf.cell(0, 15, 'Plano de Treino Personalizado', ln=True, align='C')
    pdf.ln(5)

    # Subtítulo
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, f'Nome: {nome}', ln=True)
    pdf.ln(8)

    # Corpo do plano
    for linha in linhas:
        if not linha:
            pdf.ln(4)
            continue

        # Dia/seção
        if '-' in linha and not linha[0].isdigit():
            pdf.set_fill_color(240, 240, 240)
            pdf.set_font('Arial', 'B', 13)
            pdf.set_text_color(255, 0, 0)
            # sem indent, usa largura total
            pdf.cell(0, 8, linha, ln=True, fill=True)
            pdf.ln(2)

        # Exercício (indent 8 mm)
        elif linha[0].isdigit():
            pdf.set_font('Arial', '', 11)
            pdf.set_text_color(0, 0, 0)
            indent = 8
            pdf.set_x(pdf.l_margin + indent)
            pdf.multi_cell(usable_width - indent, 6, linha)
            # não precisa de pdf.ln()

        # Dica (indent 12 mm)
        elif linha.startswith('-'):
            pdf.set_font('Arial', 'I', 10)
            pdf.set_text_color(100, 100, 100)
            indent = 12
            pdf.set_x(pdf.l_margin + indent)
            pdf.multi_cell(usable_width - indent, 5, linha)
            
        # Texto geral
        else:
            pdf.set_font('Arial', 'I', 10)
            pdf.set_text_color(80, 80, 80)
            # sem indent, usa largura total
            pdf.multi_cell(usable_width, 6, linha)

    # Rodapé
    pdf.set_y(-20)
    pdf.set_font('Arial', 'I', 9)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 5, 'Gerado por GymMind IA', align='C')

    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer.getvalue()
