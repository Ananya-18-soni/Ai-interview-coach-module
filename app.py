from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
from utils.ai_helper import generate_questions, evaluate_answer

app = Flask(__name__)
app.secret_key = "interviewcoach123"


# ---------------- DATABASE ---------------- #

def get_db():
    conn = sqlite3.connect("interview.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS interviews(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        role TEXT,
        question TEXT,
        answer TEXT,
        feedback TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()


# ---------------- AUTH ---------------- #

@app.route("/")
def home():
    return render_template("login.html")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/register_user", methods=["POST"])
def register_user():

    name = request.form["name"]
    email = request.form["email"]
    password = request.form["password"]

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO users(name,email,password) VALUES(?,?,?)",
        (name, email, password)
    )

    conn.commit()
    conn.close()

    flash("Registration Successful")
    return redirect("/")


@app.route("/login", methods=["POST"])
def login():

    email = request.form["email"]
    password = request.form["password"]

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (email, password)
    )

    user = cur.fetchone()
    conn.close()

    if user:
        session["user_id"] = user["id"]
        session["name"] = user["name"]
        return redirect("/dashboard")

    flash("Invalid Login")
    return redirect("/")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------------- DASHBOARD ---------------- #

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/")

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM interviews WHERE user_id=?",
        (session["user_id"],)
    )

    interviews = cur.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        interviews=interviews,
        name=session["name"]
    )


# ---------------- INTERVIEW ---------------- #

@app.route("/interview")
def interview_page():
    return render_template("index.html")


@app.route("/generate_questions", methods=["POST"])
def generate():

    role = request.form["role"]
    level = request.form["level"]

    questions = generate_questions(role, level)

    return render_template(
        "interview.html",
        role=role,
        questions=questions
    )


@app.route("/evaluate", methods=["POST"])
def evaluate():

    role = request.form["role"]
    question = request.form["question"]
    answer = request.form["answer"]

    feedback = evaluate_answer(
        role,
        question,
        answer
    )

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO interviews
    (user_id, role, question, answer, feedback)
    VALUES (?,?,?,?,?)
    """, (
        session["user_id"],
        role,
        question,
        answer,
        feedback
    ))

    conn.commit()
    conn.close()

    return render_template(
        "result.html",
        feedback=feedback
    )


if __name__ == "__main__":
    app.run(debug=True)
