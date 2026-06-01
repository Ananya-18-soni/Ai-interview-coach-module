from flask import Flask, render_template, request
import sqlite3
import google.generativeai as genai

app = Flask(__name__)

# Gemini API Key
genai.configure(api_key="YOUR_GEMINI_API_KEY")

model = genai.GenerativeModel("gemini-1.5-flash")

# Database setup
def init_db():
    conn = sqlite3.connect("interview.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS interviews(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT,
        question TEXT,
        answer TEXT,
        feedback TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    role = request.form["role"]

    prompt = f"""
    Generate 5 interview questions for a {role}.
    Number them properly.
    """

    response = model.generate_content(prompt)

    return render_template(
        "interview.html",
        role=role,
        questions=response.text
    )


@app.route("/evaluate", methods=["POST"])
def evaluate():

    role = request.form["role"]
    answer = request.form["answer"]

    prompt = f"""
    Evaluate this interview answer.

    Role: {role}

    Answer:
    {answer}

    Give:
    1. Score out of 10
    2. Strengths
    3. Weaknesses
    4. Suggestions
    """

    result = model.generate_content(prompt)

    feedback = result.text

    conn = sqlite3.connect("interview.db")
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO interviews
    (role,question,answer,feedback)
    VALUES (?,?,?,?)
    """, (
        role,
        "Generated Question",
        answer,
        feedback
    ))

    conn.commit()
    conn.close()

    return render_template(
        "result.html",
        feedback=feedback
    )


@app.route("/dashboard")
def dashboard():

    conn = sqlite3.connect("interview.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM interviews")

    data = cur.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        interviews=data
    )


if __name__ == "__main__":
    app.run(debug=True)
