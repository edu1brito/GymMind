import os
import json
import re
from openai import OpenAI

# Nomes dos dias em português
diass = [
    "Segunda-feira", "Terça-feira", "Quarta-feira", 
    "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"
]

# Splits de treino conforme dias
splits = {
    1: ["Full Body"],
    2: ["Parte Superior", "Parte Inferior"],
    3: ["Push (Peito/Ombro/Tríceps)", "Pull (Costas/Bíceps)", "Legs (Pernas/Glúteos)"],
    4: ["Peito/Tríceps", "Costas/Bíceps", "Ombro/Abs", "Pernas"],
    5: ["Peito", "Costas", "Pernas", "Ombro", "Braços"],
    6: ["Segunda Full", "Terça Upper", "Quarta Lower", "Quinta Full", "Sexta Upper", "Sábado Lower"],
    7: diass
}

# Inicializa cliente OpenAI usando nova interface sem organization/project
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def gerar_treino(dados: dict) -> list[dict]:
    """
    Gera um plano de treino por dias.
    Retorna lista de dicts: {'dia': str, 'exercicios': list[dict]}
    """
    dias = diass[: dados["dias_semana"]]
    split = splits.get(dados["dias_semana"], ["Full Body"])

    system = (
        "Você é um personal trainer virtual. Com base nos dados do usuário, crie um JSON válido dividido por dias da semana, "
        "sem explicações extras. Cada item deve ter 'dia' (string) e 'exercicios' (lista com objetos de 'nome','series','repeticoes')."
    )
    payload = {
        "nome": dados["nome"],
        "idade": dados["idade"],
        "peso_kg": dados["peso_kg"],
        "altura_cm": dados["altura_cm"],
        "nivel": dados["nivel"],
        "objetivo": dados["objetivo"],
        "dias_semana": dados["dias_semana"],
        "equipamentos": dados["equipamentos"],
        "restricoes": dados["restricoes"],
        "split": split,
        "dias": dias
    }

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)}
        ],
        temperature=0.7
    )
    text = response.choices[0].message.content.strip()

    match = re.search(r'\{.*\}', text, re.DOTALL)
    if not match:
        raise ValueError(f"Resposta da IA não contém JSON detectável:\n{text}")

    try:
        return json.loads(match.group(0))["treino"]
    except Exception as e:
        raise ValueError(f"Falha ao fazer parse do JSON:\n{e}\n\nConteúdo bruto:\n{text}")
