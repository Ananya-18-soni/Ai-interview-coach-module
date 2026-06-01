import os
import google.generativeai as genai

# Get API key from Railway Environment Variables
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found. Add it in Railway Variables."
    )

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")


def generate_questions(role, level):
    """
    Generate interview questions based on role and level.
    """

    prompt = f"""
    You are a professional interviewer.

    Generate exactly 5 interview questions.

    Role: {role}
    Difficulty Level: {level}

    Format:
    1.
    2.
    3.
    4.
    5.

    Return only the questions.
    """

    try:
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"Error generating questions: {str(e)}"


def evaluate_answer(role, question, answer):
    """
    Evaluate candidate answer.
    """

    prompt = f"""
    You are an expert interviewer.

    Role:
    {role}

    Interview Question:
    {question}

    Candidate Answer:
    {answer}

    Evaluate the answer and provide:

    Score: X/10

    Strengths:
    - Point 1
    - Point 2

    Weaknesses:
    - Point 1
    - Point 2

    Suggestions:
    - Point 1
    - Point 2
    """

    try:
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"Error evaluating answer: {str(e)}"


def generate_resume_questions(resume_text):
    """
    Generate interview questions from resume.
    """

    prompt = f"""
    Analyze this resume and generate:

    5 Technical Questions
    3 HR Questions
    2 Project-Based Questions

    Resume Content:
    {resume_text}
    """

    try:
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"Error processing resume: {str(e)}"
