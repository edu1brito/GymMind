from openai import OpenAI
import os

# Instancia o cliente com a chave da variável de ambiente
client = OpenAI(api_key=os.environ.get("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"))

def gerar_treino(dados: dict) -> list[dict]:
    prompt = f"""
    Crie um plano de treino personalizado para:
    - Nome: {dados['nome']}
    - Idade: {dados['idade']} anos
    - Peso: {dados['peso_kg']} kg
    - Altura: {dados['altura_cm']} cm
    - Nível: {dados['nivel']}
    - Objetivo: {dados['objetivo']}
    - Dias por semana: {dados['dias_semana']}
    - Equipamentos: {dados['equipamentos']}
    - Restrições: {dados['restricoes']}
    Formate como uma lista numerada de exercícios, cada um com número de séries e repetições. Exemplo:
    1. Agachamento – 4x8
    2. Supino reto – 3x10
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    texto = response.choices[0].message.content
    treino = []

    for linha in texto.split("\n"):
        linha = linha.strip()
        if not linha:
            continue
        partes = linha.split('.', 1)
        if len(partes) != 2:
            continue
        resto = partes[1].strip()
        if '–' in resto:
            ex, sr = resto.split('–')
        elif '-' in resto:
            ex, sr = resto.split('-', 1)
        else:
            continue
        try:
            series, reps = sr.strip().split('x')
            treino.append({
                'exercicio': ex.strip(),
                'series': int(series),
                'repeticoes': int(reps)
            })
        except:
            continue

    return treino
