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
    """
    Gera um PDF A4 com plano de treino, sem usar fontes Unicode externas.
    """
    texto_limpo = limpar_texto(texto)
    linhas = [l.strip() for l in texto_limpo.splitlines()]

    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_left_margin(10)
    pdf.set_right_margin(10)
    pdf.set_auto_page_break(auto=True, margin=15)
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
        pdf.ln(3)
        continue

    if '-' in linha and not linha[0].isdigit():
        pdf.set_font('Arial', 'B', 13)
        pdf.set_text_color(46, 134, 222)
        pdf.multi_cell(0, 8, linha)
        pdf.ln(1)

    elif linha[0].isdigit():
        pdf.set_font('Arial', '', 11)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 6, '    ' + linha)  # indentação leve
        pdf.ln(1)

    elif linha.startswith('-'):
        pdf.set_font('Arial', 'I', 10)
        pdf.set_text_color(80, 80, 80)
        pdf.multi_cell(0, 5, '      ' + linha.strip())
        pdf.ln(1)

    else:
        pdf.set_font('Arial', 'I', 10)
        pdf.set_text_color(80, 80, 80)
        pdf.multi_cell(0, 5, linha)
        pdf.ln(1)


    # Rodapé
    pdf.set_y(-20)
    pdf.set_font('Arial', 'I', 9)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 5, 'Gerado por GymMind IA', align='C')

    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer.getvalue()
