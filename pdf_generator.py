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
        "Você é um personal trainer cientificamente embasado.\n"
        f"{REFERENCIAS_CIENTIFICAS}\n"
        "Baseie-se nessas diretrizes e nos dados abaixo para montar um plano completo: \n"
        f"- Nome: {dados['nome']}\n"
        f"- Idade: {dados['idade']} anos\n"
        f"- Peso: {dados['peso_kg']} kg\n"
        f"- Altura: {dados['altura_cm']} cm\n"
        f"- Nível: {dados['nivel']}\n"
        f"- Objetivo: {dados['objetivo']}\n"
        f"- Dias/semana: {dados['dias_semana']}\n"
        f"- Equipamentos: {dados['equipamentos']}\n"
        f"- Restrições: {dados['restricoes']}\n"
        "Formato desejado:\n"
        "1) Separe por dia (ex: 'Segunda – Peito e Tríceps').\n"
        "2) Liste numerado: 'Exercício – Séries x Repetições'.\n"
        "3) Após cada dia, inclua dicas (postura, descanso, alimentação).\n"
        "4) Finalize com orientações de aquecimento, sono e hidratação."
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    texto = response.choices[0].message.content

    # Extrai lista de exercícios para possível tabela
    treino = []
    for linha in texto.splitlines():
        linha = linha.strip()
        if not linha or not linha[0].isdigit():
            continue
        partes = linha.split('.', 1)
        if len(partes) != 2:
            continue
        resto = partes[1].strip().replace('–', '-').replace('—', '-')
        if '-' not in resto:
            continue
        ex, sr = resto.split('-', 1)
        sr = sr.replace(' ', '').lower()
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


def gerar_pdf(nome: str, texto: str) -> bytes:
    """
    Gera um PDF estilizado sem sintaxe Markdown e com rodapé.

    - Título e nome em fontes diferenciadas.
    - Texto line-wrapped sem asteriscos.
    - Rodapé discreto no fim da página.
    """
    # Remove possíveis asteriscos e marcações
    texto_limpo = texto.replace('*', '')

    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()

    # Cabeçalho
    pdf.set_font('Arial', 'B', 18)
    pdf.set_text_color(46, 134, 222)
    pdf.cell(0, 10, 'Plano de Treino Personalizado', ln=True, align='C')
    pdf.ln(4)

    # Nome do usuário
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(51, 51, 51)
    pdf.cell(0, 8, f'Nome: {nome}', ln=True)
    pdf.ln(6)

    # Corpo do texto
    pdf.set_font('Arial', '', 11)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 6, texto_limpo)

    # Rodapé fixo
    pdf.set_y(-25)
    pdf.set_font('Arial', 'I', 9)
    pdf.set_text_color(136, 136, 136)
    pdf.cell(0, 6, 'Gerado por GymMind IA', ln=True, align='C')

    buffer = io.BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()


if __name__ == '__main__':
    # Exemplo rápido de uso
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
