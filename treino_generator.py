import openai

def gerar_treino(dados: dict) -> list[dict]:
    prompt = f"""
    Você é um personal trainer experiente. Com base nos dados abaixo, crie um plano de treino **completo e personalizado**:

    - Nome: {dados['nome']}
    - Idade: {dados['idade']} anos
    - Peso: {dados['peso_kg']} kg
    - Altura: {dados['altura_cm']} cm
    - Nível: {dados['nivel']}
    - Objetivo: {dados['objetivo']}
    - Dias por semana disponíveis para treinar: {dados['dias_semana']}
    - Equipamentos disponíveis: {dados['equipamentos']}
    - Restrições físicas: {dados['restricoes']}

    **Instruções para o plano:**
    - Separe o plano por dias da semana (ex: Segunda - Peito e Tríceps)
    - Para cada dia, liste os exercícios com número de séries e repetições (ex: Supino reto – 4x10)
    - Inclua dicas personalizadas com base no objetivo, nível e restrições.
    - Finalize com uma seção de orientações gerais: aquecimento, descanso, alimentação, etc.
    - Mantenha uma linguagem clara e empolgante, como se fosse para um aluno mesmo.

    **Formato de saída esperado:**
    - Títulos para cada dia (ex: "Dia 1 - Costas e Bíceps")
    - Lista numerada de exercícios (com séries e reps)
    - Dicas e instruções em parágrafos curtos após os exercícios
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    texto = response.choices[0].message.content

    # Ainda extrai os exercícios, como antes (pode usar isso pra montar tabela no PDF)
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
