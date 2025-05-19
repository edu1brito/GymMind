from openai import OpenAI
import os

# Inicializa cliente OpenAI usando variável de ambiente OPENAI_API_KEY
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Bloco fixo de referências científicas
REFERENCIAS_CIENTIFICAS = """
📚 Diretrizes científicas de referência:

ACSM (American College of Sports Medicine):
 - Iniciantes: 2–3 sessões/semana com 1–3 séries de 8–15 repetições.
 - Hipertrofia: 3–5 sessões/semana, 6–12 repetições, descanso de 60–90s.
 - Força: 3–4 sessões/semana, 3–6 repetições, descanso de 2–3min.
 - Aquecimento de 5–10 min antes de cada treino; alongamento leve pós-treino.

OMS (Organização Mundial da Saúde):
 - 150–300 min/semana de atividade moderada ou 75–150 min/semana vigorosa.
 - Combinação de exercícios aeróbicos e de resistência para saúde geral.
 - Sono de 7–9h e hidratação adequada (2–3 L/dia) como parte do programa.
"""

def gerar_treino(dados: dict) -> tuple[str, list[dict]]:
    """
    Gera um plano de treino completo em texto e retorna lista de exercícios.
    """
    # Monta o prompt incluindo as referências científicas
    prompt = f"""
Você é um personal trainer experiente e cientificamente embasado.

{REFERENCIAS_CIENTIFICAS}

Com base nos dados do usuário abaixo, elabore um plano de treino completo e seguro, alinhado a essas diretrizes:

- Nome: {dados['nome']}
- Idade: {dados['idade']} anos
- Peso: {dados['peso_kg']} kg
- Altura: {dados['altura_cm']} cm
- Nível: {dados['nivel']}
- Objetivo: {dados['objetivo']}
- Dias/semana: {dados['dias_semana']}
- Equipamentos: {dados['equipamentos']}
- Restrições: {dados['restricoes']}

**Formato**:
1) Separe por dia (ex: “Segunda – Peito e Tríceps”).
2) Liste numerado: “Exercício – Séries x Repetições” (ex: Agachamento – 4x10).
3) Após cada dia, acrescente dicas (postura, respiração, alimentação, descanso).
4) Termine com orientações gerais (aquecimento, hidratação, sono, alongamento).

Use linguagem clara, realista e motivacional.
"""

    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    texto = resp.choices[0].message.content

    # Extrai listagem de exercícios para tabela (opcional)
    treino = []
    for linha in texto.splitlines():
        linha = linha.strip()
        if not linha or not linha[0].isdigit(): continue
        partes = linha.split('.', 1)
        if len(partes) != 2: continue
        resto = partes[1].strip().replace('–','-').replace('—','-')
        if '-' not in resto: continue
        ex, sr = resto.split('-',1)
        sr = sr.replace(' ','').lower()
        if 'x' not in sr: continue
        try:
            s, r = sr.split('x')
            treino.append({'exercicio': ex.strip(), 'series': int(s), 'repeticoes': int(r)})
        except ValueError:
            continue

    return texto, treino
