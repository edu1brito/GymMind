import streamlit as st
from io import BytesIO
from treino_generator import gerar_treino
from pdf_generator import gerar_pdf
import openai
from PIL import Image
import base64

# ✅ Configuração da OpenAI
openai.api_key = st.secrets["OPENAI_API_KEY"]
openai.organization = st.secrets["OPENAI_PROJECT_ID"]

# ✅ Logo centralizada usando base64 embutida
def render_logo_centered(path):
    with open(path, "rb") as f:
        data = f.read()
        encoded = base64.b64encode(data).decode()
    st.markdown(
        f"""
        <div style="text-align: center;">
            <img src="data:image/png;base64,{encoded}" width="150"/>
            <h1 style="margin-bottom: 0;">Gym Mind</h1>
            <p style="font-size: 20px; margin-top: 0;">Gerador de Treinos</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# 🔥 Renderiza logo + título
render_logo_centered("assets/logo.png")

# ✅ Formulário
with st.form("form_ia"):
    nome = st.text_input("Seu nome")
    idade = st.number_input("Idade", min_value=10, max_value=100, value=25)
    peso_kg = st.number_input("Peso (kg)", min_value=30.0, max_value=200.0, value=70.0)
    altura_cm = st.number_input("Altura (cm)", min_value=100, max_value=250, value=170)
    nivel = st.selectbox("Nível de treino", ["Iniciante", "Intermediário", "Avançado"])
    objetivo = st.selectbox("Objetivo principal", ["Hipertrofia", "Emagrecimento", "Força", "Resistência"])
    dias_semana = st.slider("Dias disponíveis por semana", 1, 7, 3)
    equipamentos = st.text_input("Equipamentos disponíveis (separados por vírgula)", "Halteres, Banco")
    restricoes = st.text_area("Lesões ou restrições (se houver)", "Nenhuma")
    submitted = st.form_submit_button("Gerar PDF com IA")

# ✅ Processamento
if submitted:
    dados = {
        "nome": nome,
        "idade": idade,
        "peso_kg": peso_kg,
        "altura_cm": altura_cm,
        "nivel": nivel,
        "objetivo": objetivo,
        "dias_semana": dias_semana,
        "equipamentos": equipamentos,
        "restricoes": restricoes
    }

    try:
        treino = gerar_treino(dados)
        pdf_bytes = gerar_pdf(nome, treino)

        st.success("✅ Treino gerado com sucesso!")
        st.download_button(
            "📥 Baixar PDF",
            data=pdf_bytes,
            file_name=f"{nome}_treino.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"❌ Erro ao gerar o treino: {str(e)}")
