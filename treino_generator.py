import openai

client = openai.OpenAI()  # novo cliente, padrão usa API_KEY da variável de ambiente

def gerar_treino(dados: dict) -> list[dict]:
    prompt = f"""
    Você é um personal trainer experiente. Com base nos dados abaixo, crie um plano de treino completo e personalizado:

    - Nome: {dados['nome']}
    - Idade: {dados['idade']} anos
    - Peso: {dados['peso_kg']} kg
    - Altura: {dados['altura_cm']} cm
    - Nível: {dados['nivel']}
    - Objetivo: {dados['objetivo']}
    - Dias por semana disponíveis para treinar: {dados['dias_semana']}
    - Equipamentos disponíveis: {dados['equipamentos']}
    - Restrições físicas: {dados['restricoes']}

    Instruções:
    - Separe o plano por dias da semana (ex: Segunda - Peito e Tríceps)
    - Liste os exercícios com séries e repetições
    - Dê dicas personalizadas
    - Finalize com orientações gerais (aquecimento, descanso etc.)
    """

    response = client.chat.completions.create(
        model="gpt-4o",
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
        if 'x' not in sr:
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
