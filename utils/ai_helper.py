import os
import google.generativeai as genai

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise Exception("GEMINI_API_KEY not found in Railway Variables")

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")


def generate_questions(role, level):

    prompt = f"""
    Generate 5 interview questions.

    Role: {role}
    Level: {level}

    Return only questions.
    """

    response = model.generate_content(prompt)

    return response.text


def evaluate_answer(role, question, answer):

    prompt = f"""
    Evaluate this answer.

    Role:
    {role}

    Question:
    {question}

    Answer:
    {answer}

    Give:

    Score /10

    Strengths

    Weaknesses

    Suggestions
    """

    response = model.generate_content(prompt)

    return response.text
