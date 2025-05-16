import openai

def gerar_plano_completo(dados: dict) -> str:
    prompt = f"""
    Você é um personal trainer. Crie um plano de treino personalizado para o(a) aluno(a) abaixo com base nos dados:
    - Nome: {dados['nome']}
    - Idade: {dados['idade']} anos
    - Peso: {dados['peso_kg']} kg
    - Altura: {dados['altura_cm']} cm
    - Nível de experiência: {dados['nivel']}
    - Objetivo: {dados['objetivo']}
    - Quantidade de dias por semana disponível para treino: {dados['dias_semana']}
    - Equipamentos disponíveis: {dados['equipamentos']}
    - Restrições físicas ou limitações: {dados['restricoes']}

    **Instruções:**
    - Separe os treinos por dia da semana, de acordo com os dias disponíveis.
    - Organize cada dia com os grupos musculares focados e exercícios com número de séries e repetições.
    - Dê um nome para cada dia (ex: "Dia 1 - Peito e Tríceps").
    - Inclua dicas específicas com base nas restrições, nível e objetivo.
    - Use uma formatação clara com títulos, subtítulos e marcadores.

    Ao final, inclua uma seção com orientações gerais (ex: aquecimento, descanso, alimentação básica).
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content
