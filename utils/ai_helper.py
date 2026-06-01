import google.generativeai as genai

genai.configure(api_key="YOUR_GEMINI_API_KEY")

model = genai.GenerativeModel("gemini-1.5-flash")


def generate_questions(role, level):
    prompt = f"""
    Generate 5 interview questions.

    Role: {role}
    Level: {level}

    Return numbered questions only.
    """

    response = model.generate_content(prompt)
    return response.text


def evaluate_answer(role, question, answer):
    prompt = f"""
    Evaluate this interview answer.

    Role: {role}

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
