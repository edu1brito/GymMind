from fpdf import FPDF
import io

def gerar_pdf(nome: str, treino: list[dict]) -> bytes:
    # Inicializa PDF
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()

    # Cabeçalho
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(46, 134, 222)  # azul suave
    pdf.cell(0, 10, 'Plano de Treino Personalizado', ln=True, align='C')
    pdf.ln(4)

    # Nome do usuário
    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(51, 51, 51)
    pdf.cell(0, 8, f'Nome: {nome}', ln=True)
    pdf.ln(4)

    # Título da seção de exercícios
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(44, 62, 80)
    pdf.cell(0, 8, 'Exercícios:', ln=True)
    pdf.ln(2)

    # Cabeçalho da tabela
    pdf.set_font('Arial', 'B', 12)
    pdf.set_fill_color(223, 240, 255)  # fundo azul claro
    pdf.cell(100, 8, 'Exercício', border=1, align='C', fill=True)
    pdf.cell(30, 8, 'Séries', border=1, align='C', fill=True)
    pdf.cell(30, 8, 'Repetições', border=1, align='C', fill=True, ln=True)

    # Linhas de exercícios
    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(0, 0, 0)
    for item in treino:
        nome_ex = item.get('exercicio', '')
        series = item.get('series', '')
        reps = item.get('repeticoes', '')
        pdf.cell(100, 8, nome_ex, border=1)
        pdf.cell(30, 8, str(series), border=1, align='C')
        pdf.cell(30, 8, str(reps), border=1, align='C', ln=True)

    # Rodapé
    pdf.ln(6)
    pdf.set_font('Arial', 'I', 10)
    pdf.set_text_color(136, 136, 136)
    pdf.cell(0, 10, 'Gerado por GymMind IA ', align='C')

    # Gera bytes do PDF
    buffer = io.BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()
