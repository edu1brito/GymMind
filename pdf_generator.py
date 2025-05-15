from fpdf import FPDF
import io

def gerar_pdf(nome: str, treino: list[dict]) -> bytes:
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()

    # Cabeçalho
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(46, 134, 222)
    pdf.cell(0, 10, f"Plano de Treino Personalizado", ln=True, align="C")

    pdf.ln(2)
    pdf.set_font("Arial", "", 12)
    pdf.set_text_color(51, 51, 51)
    pdf.cell(0, 8, f"Nome: {nome}", ln=True)

    # Corpo: um bloco por dia
    for dia in treino:
        # Título do dia
        pdf.ln(4)
        pdf.set_font("Arial", "B", 14)
        pdf.set_fill_color(241, 241, 241)
        pdf.cell(0, 8, dia["dia"], ln=True, fill=True)

        # Cabeçalho da tabela
        pdf.set_font("Arial", "B", 12)
        pdf.set_fill_color(223, 240, 255)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(100, 8, "Exercício", border=1, align="C", fill=True)
        pdf.cell(30, 8, "Séries", border=1, align="C", fill=True)
        pdf.cell(30, 8, "Repetições", border=1, align="C", fill=True, ln=True)

        # Linhas de exercícios
        pdf.set_font("Arial", "", 12)
        pdf.set_text_color(0, 0, 0)
        for ex in dia["exercicios"]:
            pdf.cell(100, 8, ex["nome"], border=1)
            pdf.cell(30, 8, str(ex["series"]), border=1, align="C")
            pdf.cell(30, 8, str(ex["repeticoes"]), border=1, align="C", ln=True)

    # Rodapé
    pdf.ln(6)
    pdf.set_font("Arial", "I", 10)
    pdf.set_text_color(136, 136, 136)
    pdf.cell(0, 10, "Gerado por GymMind IA 💪", align="C")

    # Gera bytes
    buffer = io.BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()
