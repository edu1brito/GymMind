from openai import OpenAI
import os
from fpdf import FPDF
import io

# Inicializa cliente OpenAI
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def gerar_treino(dados: dict) -> tuple[str, list[dict]]:
    """
    Gera o plano completo em texto e retorna uma lista estruturada dos exercícios.
    Retorna:
      - texto: string com dias da semana, exercícios, dicas e orientações.
      - treino: lista de dicts com chaves 'exercicio', 'series', 'repeticoes'.
    """
    prompt = f"""
Você é um personal trainer experiente. Com base nos dados abaixo, crie um **plano de treino completo**:

- Nome: {dados['nome']}
- Idade: {dados['idade']} anos
- Peso: {dados['peso_kg']} kg
- Altura: {dados['altura_cm']} cm
- Nível: {dados['nivel']}
- Objetivo: {dados['objetivo']}
- Dias por semana: {dados['dias_semana']}
- Equipamentos: {dados['equipamentos']}
- Restrições: {dados['restricoes']}

**Instruções de formatação**:
1. Separe o plano por dia da semana (ex: “Segunda – Peito e Tríceps”).
2. Para cada dia, liste **numerado**:
   - Exercício – Séries x Repetições
3. Ao final de cada dia, acrescente **dicas personalizadas** (álcool, sono, alimentação, postura, etc.).
4. Inclua uma seção final de **orientações gerais** (aquecimento, descanso, hidratação).

Use linguagem clara e motivacional.
    """

    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    texto = resp.choices[0].message.content

    # Extrai somente a listagem de exercícios para tabela
    treino = []
    for linha in texto.splitlines():
        line = linha.strip()
        if not line or not line[0].isdigit():
            continue
        partes = line.split('.', 1)
        if len(partes) != 2:
            continue
        resto = partes[1].strip()
        if '–' in resto:
            ex, sr = resto.split('–', 1)
        elif '-' in resto:
            ex, sr = resto.split('-', 1)
        else:
            continue
        sr = sr.lower().replace(' ', '')
        if 'x' not in sr:
            continue
        try:
            s, r = sr.split('x')
            treino.append({
                'exercicio': ex.strip(),
                'series': int(s),
                'repeticoes': int(r)
            })
        except ValueError:
            continue

    return texto, treino


def gerar_pdf(nome: str, texto: str, treino: list[dict]) -> bytes:
    """
    Gera um PDF com o plano completo em texto e uma tabela de exercícios.
    """
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()

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
    return buffer.getvalue()
