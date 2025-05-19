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

def gerar_pdf(nome: str, texto: str, treino: list[dict]) -> bytes:
    """
    Gera um PDF com o plano completo em texto, tabela de exercícios
    e logo centralizada no topo.
    """
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()

    # --- Logo centralizada ---
    # Carrega a imagem e centraliza pela largura da página.
    logo_path = "assets/logo.png"
    logo_width = 40  # largura em mm (ajuste conforme o seu logo)
    x_pos = (pdf.w - logo_width) / 2
    y_pos = 10
    pdf.image(logo_path, x=x_pos, y=y_pos, w=logo_width)
    pdf.ln(logo_width + 5)  # pula abaixo da logo

    # Cabeçalho
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(46, 134, 222)
    pdf.cell(0, 10, 'Plano de Treino Personalizado', ln=True, align='C')
    pdf.ln(4)

    # Nome do usuário
    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(51, 51, 51)
    pdf.cell(0, 8, f'Nome: {nome}', ln=True)
    pdf.ln(6)

    # Texto completo do plano
    pdf.set_font('Arial', '', 11)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 6, texto)
    pdf.ln(8)

    # Seção de tabela de exercícios
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(44, 62, 80)
    pdf.cell(0, 8, 'Tabela de Exercícios', ln=True)
    pdf.ln(2)

    # Cabeçalho da tabela
    pdf.set_font('Arial', 'B', 12)
    pdf.set_fill_color(223, 240, 255)
    pdf.cell(100, 8, 'Exercício', border=1, align='C', fill=True)
    pdf.cell(30, 8, 'Séries', border=1, align='C', fill=True)
    pdf.cell(30, 8, 'Repetições', border=1, align='C', fill=True, ln=True)

    # Linhas de exercícios
    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(0, 0, 0)
    for item in treino:
        pdf.cell(100, 8, item.get('exercicio', ''), border=1)
        pdf.cell(30, 8, str(item.get('series', '')), border=1, align='C')
        pdf.cell(30, 8, str(item.get('repeticoes', '')), border=1, align='C', ln=True)

    # Rodapé
    pdf.ln(6)
    pdf.set_font('Arial', 'I', 10)
    pdf.set_text_color(136, 136, 136)
    pdf.cell(0, 10, 'Gerado por GymMind IA', align='C')

    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer.getvalue()
