import streamlit as st
from openai import OpenAI
from fpdf import FPDF
import io
import os
import base64

# --- Configuração OpenAI ---
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# --- Funções geradoras ---

def gerar_treino(dados: dict) -> tuple[str, list[dict]]:
    """
    Gera um plano de treino completo em texto e uma lista estruturada de exercícios.
    Retorna:
      - texto: plano com dias, exercícios, dicas e orientações.
      - treino: lista de {'exercicio','series','repeticoes'} para tabela (não mais usada).
    """
    prompt = f"""
Você é um personal trainer experiente e atualizado com as diretrizes da ACSM (American College of Sports Medicine) e da OMS (Organização Mundial da Saúde).

Com base nos dados abaixo, elabore um plano de treino completo e seguro, alinhado com boas práticas científicas:

- Nome: {dados['nome']}
- Idade: {dados['idade']} anos
- Peso: {dados['peso_kg']} kg
- Altura: {dados['altura_cm']} cm
- Nível de experiência: {dados['nivel']}
- Objetivo: {dados['objetivo']}
- Dias por semana: {dados['dias_semana']}
- Equipamentos disponíveis: {dados['equipamentos']}
- Restrições ou lesões: {dados['restricoes']}

Requisitos do plano:
1. Separe o plano por dia da semana (ex: “Segunda – Peito e Tríceps”).
2. Para cada dia, liste os exercícios **numerados** com o formato:  
   - Exercício – Séries x Repetições (ex: Supino reto – 4x10)
3. Após cada dia, inclua **dicas personalizadas** sobre postura, alimentação, hidratação, descanso, ou variações.
4. Finalize com uma seção de *orientações gerais* que incluam aquecimento, descanso entre treinos, sono e hidratação — tudo baseado em recomendações da ACSM e OMS.

Use linguagem clara, encorajadora e profissional. Evite exageros e foque em segurança, consistência e adaptação progressiva.
"""

    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role":"user","content":prompt}],
        temperature=0.7
    )
    texto = resp.choices[0].message.content

    # A lista de exercícios não é utilizada no PDF, mas pode ser retornada para outras finalidades
    treino = []
    for line in texto.splitlines():
        if not line.strip() or not line[0].isdigit():
            continue
        parts = line.split('.', 1)
        resto = parts[1].strip() if len(parts) == 2 else ''
        resto = resto.replace('–', '-').replace('—', '-')
        if '-' in resto:
            ex, sr = resto.split('-', 1)
        else:
            continue
        sr = sr.replace(' ', '').lower()
        if 'x' not in sr:
            continue
        try:
            s, r = sr.split('x')
            treino.append({'exercicio': ex.strip(), 'series': int(s), 'repeticoes': int(r)})
        except:
            continue
    return texto, treino


def gerar_pdf(nome: str, texto: str, treino: list[dict]) -> bytes:
    """
    Gera PDF com:
      - título e nome
      - texto completo do plano
      - rodapé com referências (sem tabela)
    """
    texto_pdf = texto.replace('–', '-').replace('—', '-')

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
    pdf.multi_cell(0, 6, texto_pdf)

    # Rodapé fixo no final da página
    pdf.set_y(-30)
    pdf.set_font('Arial', 'I', 10)
    pdf.set_text_color(136, 136, 136)
    pdf.cell(0, 8, 'Gerado por GymMind IA', ln=True, align='C')
    pdf.set_font('Arial', 'I', 9)
    pdf.multi_cell(0, 6,
        "Referências utilizadas:\n"
        "- ACSM: Guidelines for Exercise Testing and Prescription\n"
        "- OMS: Recomendação Global de Atividade Física para a Saúde"
    )

    buf = io.BytesIO()
    pdf.output(buf)
    return buf.getvalue()

# --- Streamlit App ---
def render_logo(path):
    data = open(path, 'rb').read()
    enc = base64.b64encode(data).decode()
    st.markdown(f"""
    <div style='text-align:center'>
      <img src='data:image/png;base64,{enc}' width='150'/>
      <h1>Gym Mind</h1>
      <h3>Gerador de Treinos</h3>
    </div>
    """, unsafe_allow_html=True)

st.set_page_config(page_title='Gym Mind', layout='centered')
render_logo('assets/logo.png')

with st.form('form'):
    nome = st.text_input('Nome')
    idade = st.number_input('Idade', 10, 100, 25)
    peso = st.number_input('Peso (kg)', 30.0, 200.0, 70.0)
    altura = st.number_input('Altura (cm)', 100, 250, 170)
    nivel = st.selectbox('Nível', ['Iniciante', 'Intermediário', 'Avançado'])
    objetivo = st.selectbox('Objetivo', ['Hipertrofia', 'Emagrecimento', 'Força', 'Resistência'])
    dias = st.slider('Dias por semana', 1, 7, 3)
    equips = st.text_input('Equip. disponíveis', 'Halteres, Banco')
    restr = st.text_area('Lesões/Restrições', 'Nenhuma')
    submit = st.form_submit_button('Gerar PDF')

if submit:
    dados = {
        'nome': nome,
        'idade': idade,
        'peso_kg': peso,
        'altura_cm': altura,
        'nivel': nivel,
        'objetivo': objetivo,
        'dias_semana': dias,
        'equipamentos': equips,
        'restricoes': restr
    }
    try:
        texto_plano, lista_treino = gerar_treino(dados)
        pdf_bytes = gerar_pdf(nome, texto_plano, lista_treino)
        st.success('✅ Treino gerado com sucesso!')
        st.download_button('📥 Baixar PDF', data=pdf_bytes,
                           file_name=f'{nome}_plano.pdf', mime='application/pdf')
    except Exception as e:
        st.error(f'Erro: {e}')
