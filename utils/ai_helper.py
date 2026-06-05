import os
import google.generativeai as genai

API_KEY = os.getenv("GEMINI_API_KEY")

model = None

if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        print("Gemini initialized successfully")
    except Exception as e:
        print(f"Gemini initialization failed: {e}")
else:
    print("GEMINI_API_KEY not found")


def generate_questions(role, level):

    if model is None:
        return """
1. Tell me about yourself.
2. What are your strengths?
3. What are your weaknesses?
4. Why should we hire you?
5. Where do you see yourself in 5 years?
"""

    try:
        prompt = f"""
Generate 5 interview questions.

Role: {role}
Level: {level}

Return only questions.
"""

        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        print(f"Question Generation Error: {e}")
        return "Unable to generate questions."


def evaluate_answer(role, question, answer):

    if model is None:
        return """
Score: 7/10

Strengths:
- Good attempt

Weaknesses:
- Needs more detail

Suggestions:
- Add practical examples
"""

    try:
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

    except Exception as e:
        print(f"Evaluation Error: {e}")
        return f"Evaluation failed: {str(e)}"
