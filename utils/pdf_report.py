from fpdf import FPDF


def generate_report(role, feedback, filename):

    pdf = FPDF()

    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "AI Interview Report", ln=True)

    pdf.ln(10)

    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(
        0,
        10,
        f"Role: {role}\n\nFeedback:\n{feedback}"
    )

    pdf.output(filename)
