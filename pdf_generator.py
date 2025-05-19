from openai import OpenAI
import os
from fpdf import FPDF
import io

# Inicializa cliente OpenAI
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Bloco de referências científicas fixas
REFERENCIAS_CIENTIFICAS = (
    "Diretrizes Científicas de Referência:\n"
    "- ACSM: 1–3 séries de 8–15 repetições para iniciantes; 6–12 repetições para hipertrofia; 3–6 repetições para força.\n"
    "- Aquecimento: 5–10 minutos antes de treinos; alongamento leve após.\n"
    "- OMS: 150–300 minutos de atividade moderada por semana; 7–9 horas de sono; 2–3 L de hidratação diária.\n"
)

def gerar_treino(dados: dict) -> tuple[str, list[dict]]:
    """
    Gera um plano de treino completo em texto e retorna uma lista de exercícios.

    Retorna:
        texto: plano completo formatado por dia e orientações.
        treino: lista de dicts com chaves 'exercicio', 'series', 'repeticoes'.
    """
    prompt = (
        "Você é um personal trainer experiente e cientificamente embasado."
        "
        Não utilize nenhuma sintaxe Markdown ou asteriscos na sua resposta."
        f"{REFERENCIAS_CIENTIFICAS}
"
        "Com base nessas diretrizes e nos dados abaixo, monte um plano completo e claro sem formatação Markdown:
"
        f"- Nome: {dados['nome']}
"
        f"- Idade: {dados['idade']} anos
"
        f"- Peso: {dados['peso_kg']} kg
"
        f"- Altura: {dados['altura_cm']} cm
"
        f"- Nível: {dados['nivel']}
"
        f"- Objetivo: {dados['objetivo']}
"
        f"- Dias/semana: {dados['dias_semana']}
"
        f"- Equipamentos: {dados['equipamentos']}
"
        f"- Restrições: {dados['restricoes']}
"
        "Formato desejado:
"
        "Dia da semana – Treino (ex: Segunda – Peito e Tríceps).
"
        "Em cada dia, listagem numerada: Exercício – Séries x Repetições.
"
        "Após a listagem, inclua a seção Dicas Personalizadas sem usar marcadores '*':
"
        "Dicas Personalizadas:
"
        "- texto da dica
"
        "Finalize com orientações gerais."
    ).\n"
        "Em cada dia, listagem numerada: Exercício – Séries x Repetições.\n"
        "Após listagem, inclua seção 'Dicas personalizadas:' com bullets.\n"
        "Finalize com orientações gerais."
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content, []


def gerar_pdf(nome: str, texto: str) -> bytes:
    """
    Gera um PDF estilizado sem sintaxe Markdown, com formatação de títulos,
    itens numerados e dicas em itálico.
    """
    # Limpa markdown e asteriscos
    texto_limpo = texto.replace('*', '').replace('**', '')
    lines = texto_limpo.splitlines()

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
    pdf.ln(4)

    # Corpo
    for line in lines:
        text = line.strip()
        if not text:
            pdf.ln(2)
            continue
        # Cabeçalhos de dia (contêm '–' e não iniciam com número)
        if '–' in text and not text[0].isdigit():
            pdf.set_font('Arial', 'B', 13)
            pdf.set_text_color(46, 134, 222)
            pdf.cell(0, 8, text, ln=True)
            pdf.ln(1)
        # Dicas personalizadas
        elif text.lower().startswith('dicas'):
            pdf.ln(2)
            pdf.set_font('Arial', 'B', 12)
            pdf.set_text_color(34, 34, 34)
            pdf.cell(0, 7, 'Dicas Personalizadas:', ln=True)
            pdf.ln(1)
        # Itens numerados
        elif text[0].isdigit():
            pdf.set_font('Arial', '', 11)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(5)
            pdf.multi_cell(0, 6, text)
        # Bullets de dicas
        elif text.startswith('-'):
            pdf.set_font('Arial', 'I', 10)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(10)
            pdf.multi_cell(0, 5, f'• {text[1:].strip()}')
        # Orientações gerais
        else:
            pdf.ln(1)
            pdf.set_font('Arial', 'I', 10)
            pdf.set_text_color(80, 80, 80)
            pdf.multi_cell(0, 5, text)

    # Rodapé
    pdf.set_y(-20)
    pdf.set_font('Arial', 'I', 9)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 5, 'Gerado por GymMind IA', align='C')

    buf = io.BytesIO()
    pdf.output(buf)
    return buf.getvalue()


if __name__ == '__main__':
    dados_exemplo = {
        'nome': 'Teste',
        'idade': 25,
        'peso_kg': 70,
        'altura_cm': 170,
        'nivel': 'Iniciante',
        'objetivo': 'Emagrecimento',
        'dias_semana': 3,
        'equipamentos': 'Halteres',
        'restricoes': 'Nenhuma'
    }
    texto, _ = gerar_treino(dados_exemplo)
    pdf_bytes = gerar_pdf(dados_exemplo['nome'], texto)
    with open('plano_example.pdf', 'wb') as f:
        f.write(pdf_bytes)
    print('PDF gerado: plano_example.pdf')
