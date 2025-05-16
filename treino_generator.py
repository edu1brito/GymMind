from openai import OpenAI
import os
from fpdf import FPDF
import io

# Inicializa cliente OpenAI usando variável de ambiente OPENAI_API_KEY
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def gerar_treino(dados: dict) -> tuple[str, list[dict]]:
    """
    Gera um plano de treino completo em texto e retorna também uma lista estruturada de exercícios.

    Retorna:
        texto: string contendo dias da semana, exercícios numerados, dicas e orientações gerais.
        treino: lista de dicionários com chaves 'exercicio', 'series', 'repeticoes' para uso em tabela.
    """
    prompt = f"""
Você é um personal trainer experiente. Com base nos dados abaixo, elabore um plano de treino completo e motivacional:

- Nome: {dados['nome']}
- Idade: {dados['idade']} anos
- Peso: {dados['peso_kg']} kg
- Altura: {dados['altura_cm']} cm
- Nível de experiência: {dados['nivel']}
- Objetivo: {dados['objetivo']}
- Dias disponíveis por semana: {dados['dias_semana']}
- Equipamentos disponíveis: {dados['equipamentos']}
- Restrições ou lesões: {dados['restricoes']}

**Formatação esperada**:
1. Separe o plano por dia da semana (ex: "Segunda – Peito e Tríceps").
2. Para cada dia, utilize lista numerada:
   - Exercício – Séries x Repetições (ex: Agachamento – 4x10)
3. Ao final de cada dia, adicione dicas personalizadas (postura, respiração, alimentação, descanso).
4. Inclua ao final uma seção de orientações gerais (aquecimento, alongamento, hidratação).

Use linguagem clara, amigável e motivacional.
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    texto = response.choices[0].message.content

    # Extrai apenas a listagem de exercícios para tabela
    treino = []
    for linha in texto.splitlines():
        linha = linha.strip()
        if not linha or not linha[0].isdigit():
            continue
        partes = linha.split('.', 1)
        if len(partes) != 2:
            continue
        resto = partes[1].strip()
        # separadores válidos
        if '–' in resto:
            ex, sr = resto.split('–', 1)
        elif '-' in resto:
            ex, sr = resto.split('-', 1)
        else:
            continue
        sr = sr.replace(' ', '').lower()
        if 'x' not in sr:
            continue
        try:
            series_str, reps_str = sr.split('x')
            treino.append({
                'exercicio': ex.strip(),
                'series': int(series_str),
                'repeticoes': int(reps_str)
            })
        except ValueError:
            continue

    return texto, treino


def gerar_pdf(nome: str, texto: str, treino: list[dict]) -> bytes:
    """
    Gera um PDF com:
      - título e nome do usuário
      - texto completo do plano (dias, exercícios e dicas)
      - tabela de exercícios
      - rodapé de crédito
    """
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()

    # Cabeçalho
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(46, 134, 222)
    pdf.cell(0, 10, 'Plano de Treino Personalizado', ln=True, align='C')
    pdf.ln(4)

    # Nome
    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(51, 51, 51)
    pdf.cell(0, 8, f'Nome: {nome}', ln=True)
    pdf.ln(6)

    # Texto completo
    pdf.set_font('Arial', '', 11)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 6, texto)
    pdf.ln(8)

    # Tabela de exercícios
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(44, 62, 80)
    pdf.cell(0, 8, 'Tabela de Exercícios', ln=True)
    pdf.ln(2)

    pdf.set_font('Arial', 'B', 12)
    pdf.set_fill_color(223, 240, 255)
    pdf.cell(100, 8, 'Exercício', border=1, align='C', fill=True)
    pdf.cell(30, 8, 'Séries', border=1, align='C', fill=True)
    pdf.cell(30, 8, 'Repetições', border=1, align='C', fill=True, ln=True)

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
