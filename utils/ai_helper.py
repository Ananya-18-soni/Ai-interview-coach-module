import os
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
else:
    model = None


def generate_questions(role, level):

    if not model:
        return [
            "Tell me about yourself.",
            "What are your strengths?",
            "Why should we hire you?"
        ]

    prompt = f"""
    Generate 5 interview questions for a {level} {role}.
    Return only questions.
    """

    response = model.generate_content(prompt)

    return response.text.split("\n")


def evaluate_answer(role, question, answer):

    if not model:
        return "AI evaluation unavailable."

    prompt = f"""
    Role: {role}

    Question:
    {question}

    Answer:
    {answer}

    Evaluate the answer and give feedback.
    """

    response = model.generate_content(prompt)

    return response.text
