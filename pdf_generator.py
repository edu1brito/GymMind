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
Você é um personal trainer experiente e atualizado com as diretrizes da ACSM (American College of Sports Medicine) e da OMS (Organização Mundial da Saúde).

Com base nos dados abaixo, elabore um **plano de treino completo e seguro**, alinhado com boas práticas científicas:

- Nome: {dados['nome']}
- Idade: {dados['idade']} anos
- Peso: {dados['peso_kg']} kg
- Altura: {dados['altura_cm']} cm
- Nível de experiência: {dados['nivel']}
- Objetivo: {dados['objetivo']}
- Dias por semana: {dados['dias_semana']}
- Equipamentos disponíveis: {dados['equipamentos']}
- Restrições ou lesões: {dados['restricoes']}

**Requisitos do plano**:
1. Separe o plano por dia da semana (ex: “Segunda – Peito e Tríceps”).
2. Para cada dia, liste os exercícios **numerados** com o formato:  
   - Exercício – Séries x Repetições (ex: Supino reto – 4x10)
3. Após cada dia, inclua **dicas personalizadas** sobre postura, alimentação, hidratação, descanso, ou variações.
4. Finalize com uma seção de **orientações gerais** que incluam aquecimento, descanso entre treinos, sono e hidratação — tudo baseado em recomendações da ACSM e OMS.

Use linguagem clara, encorajadora e profissional. Evite exageros e foque em segurança, consistência e adaptação progressiva.
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




    # Rodapé fixo no final da página
    pdf.set_y(-35)
    pdf.set_font('Arial', 'I', 10)
    pdf.set_text_color(136, 136, 136)
    pdf.cell(0, 6, 'Gerado por GymMind IA', ln=True, align='C')

    pdf.set_font('Arial', 'I', 9)
    pdf.multi_cell(0, 5,
        "Referências utilizadas:\n"
        "- ACSM: Guidelines for Exercise Testing and Prescription\n"
        "- OMS: Recomendação Global de Atividade Física para a Saúde"
    )

    buffer = io.BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()


if __name__ == "__main__":
    # Exemplo de uso rápido
    dados_exemplo = {
        'nome': 'Fulano',
        'idade': 30,
        'peso_kg': 75,
        'altura_cm': 175,
        'nivel': 'Intermediário',
        'objetivo': 'Hipertrofia',
        'dias_semana': 4,
        'equipamentos': 'Halteres, Banco',
        'restricoes': 'Nenhuma'
    }
    texto, treino = gerar_treino(dados_exemplo)
    pdf_bytes = gerar_pdf(dados_exemplo['nome'], texto, treino)
    with open("plano_exemplo.pdf", "wb") as f:
        f.write(pdf_bytes)
    print("PDF de exemplo gerado: plano_exemplo.pdf")
