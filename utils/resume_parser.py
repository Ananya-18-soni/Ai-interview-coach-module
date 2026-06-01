from PyPDF2 import PdfReader


def extract_resume_text(filepath):

    text = ""

    reader = PdfReader(filepath)

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text

    return text
