import streamlit as st
import base64
from treino_generator import gerar_treino
from pdf_generator import gerar_pdf

# --- Streamlit App ---
st.set_page_config(page_title='Gym Mind', layout='centered')

def render_logo(path):
    with open(path, 'rb') as f:
        data = f.read()
    enc = base64.b64encode(data).decode()
    st.markdown(f"""
    <div style='text-align:center'>
      <img src='data:image/png;base64,{enc}' width='150'/>
      <h1>Gym Mind</h1>
      <h3>Gerador de Treinos</h3>
    </div>
    """, unsafe_allow_html=True)

render_logo('assets/logo.png')

with st.form('form'):
    nome = st.text_input('Nome')
    idade = st.number_input('Idade', 10, 100, 25)
    peso = st.number_input('Peso (kg)', 30.0, 200.0, 70.0)
    altura = st.number_input('Altura (cm)', 100, 250, 170)
    nivel = st.selectbox('Nível', ['Iniciante', 'Intermediário', 'Avançado'])
    objetivo = st.selectbox('Objetivo', ['Hipertrofia', 'Emagrecimento', 'Força', 'Resistência'])
    dias = st.slider('Dias por semana', 1, 7, 3)
    equips = st.text_input('Equipamentos disponíveis', 'Halteres, Banco')
    restr = st.text_area('Lesões e Restrições', 'Nenhuma')
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
        pdf_bytes = gerar_pdf(nome, texto_plano)
        st.success('✅ Treino gerado com sucesso!')
        st.download_button(
            label='📥 Baixar PDF',
            data=pdf_bytes,
            file_name=f'{nome}_plano.pdf',
            mime='application/pdf'
        )
    except Exception as e:
        st.error(f'Erro: {e}')
