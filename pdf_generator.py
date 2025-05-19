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

def gerar_pdf(nome: str, texto: str, treino: list[dict] | None = None) -> bytes:
    """
    Gera um PDF com o plano completo em texto e, opcionalmente, uma tabela de exercícios.
    """
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()

    # --- Logo, cabeçalho etc ---

    # Texto completo do plano
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 6, texto)
    pdf.ln(8)

    # Se me passou a lista de treino, roda a tabela; se não, pula essa parte
    if treino:
        # ... seu bloco de geração da tabela …
    ```

Por exemplo:

```python
def gerar_pdf(nome: str, texto: str, treino: list[dict] | None = None) -> bytes:
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()

    # --- Logo e cabeçalho (conforme mostrado antes) …

    # Texto
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 6, texto)
    pdf.ln(8)

    # Tabela apenas se treino não for None
    if treino:
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 8, 'Tabela de Exercícios', ln=True)
        pdf.ln(2)

        # Cabeçalho da tabela
        pdf.set_font('Arial', 'B', 12)
        pdf.set_fill_color(223, 240, 255)
        pdf.cell(100, 8, 'Exercício', border=1, align='C', fill=True)
        pdf.cell(30, 8, 'Séries', border=1, align='C', fill=True)
        pdf.cell(30, 8, 'Repetições', border=1, align='C', fill=True, ln=True)

        # Linhas:
        pdf.set_font('Arial', '', 12)
        for item in treino:
            pdf.cell(100, 8, item['exercicio'], border=1)
            pdf.cell(30, 8, str(item['series']), border=1, align='C')
            pdf.cell(30, 8, str(item['repeticoes']), border=1, align='C', ln=True)

    # Rodapé…
    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer.getvalue()
