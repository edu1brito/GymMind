import openai
import json

# Nomes dos dias em português
DIAS_SEMANA = [
    "Segunda-feira", "Terça-feira", "Quarta-feira", 
    "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"
]

# Splits de treino conforme dias
SPLITS = {
    1: ["Full Body"],
    2: ["Parte Superior", "Parte Inferior"],
    3: ["Push (Peito/Ombro/Tríceps)", "Pull (Costas/Bíceps)", "Legs (Pernas/Glúteos)"],
    4: ["Peito/Tríceps", "Costas/Bíceps", "Ombro/Abs", "Pernas"],
    5: ["Peito", "Costas", "Pernas", "Ombro", "Braços"],
    6: ["Segunda Full", "Terça Upper", "Quarta Lower", "Quinta Full", "Sexta Upper", "Sábado Lower"],
    7: DIAS_SEMANA
}


def gerar_treino(dados: dict) -> list[dict]:
    """
    Gera um plano de treino estruturado por dias da semana.
    Retorna uma lista de objetos: {"dia": str, "exercicios": [{"nome", "series", "repeticoes"}, ...]}
    """
    dias = DIAS_SEMANA[: dados["dias_semana"]]
    split = SPLITS.get(dados["dias_semana"], ["Full Body"])

    system_prompt = (
        "Você é um personal trainer virtual. "
        "Com base nos dados do usuário, crie um JSON com o plano de treino dividido em dias. "
        "Cada dia deve ter um nome (campo 'dia') e uma lista 'exercicios' com itens contendo 'nome', 'series' e 'repeticoes'."
    )
    user_prompt = {
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
    prompt_content = (
        f"Usuário: {json.dumps(user_prompt, ensure_ascii=False)}\n"
        "Responda somente com um JSON válido, sem explicações extras."
    )

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt_content}
        ],
        temperature=0.7,
    )
    text = response.choices[0].message.content.strip()
    # Parse JSON
    try:
        treino = json.loads(text)
    except json.JSONDecodeError:
        # fallback: return empty list ou raise
        raise ValueError("Resposta da IA não está em JSON válido:\n" + text)
    return treino
