from flask import Flask, render_template, request, redirect, session, flash, send_file
import sqlite3
import os

from utils.ai_helper import generate_questions, evaluate_answer
from utils.resume_parser import extract_resume_text
from utils.pdf_report import generate_report

app = Flask(__name__)
app.secret_key = "interviewcoach123"

UPLOAD_FOLDER = "static/uploads"
REPORT_FOLDER = "reports"

# Create folders only if they don't already exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(REPORT_FOLDER):
    os.makedirs(REPORT_FOLDER)


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

    try:
        cur.execute(
            "INSERT INTO users(name,email,password) VALUES(?,?,?)",
            (name, email, password)
        )
        conn.commit()

    except:
        flash("Email already exists")

    conn.close()

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
def interview():

    if "user_id" not in session:
        return redirect("/")

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

    session["last_role"] = role
    session["last_feedback"] = feedback

    return render_template(
        "result.html",
        feedback=feedback
    )


# ---------------- RESUME UPLOAD ---------------- #

@app.route("/upload_resume", methods=["POST"])
def upload_resume():

    resume = request.files["resume"]

    filepath = os.path.join(
        UPLOAD_FOLDER,
        resume.filename
    )

    resume.save(filepath)

    resume_text = extract_resume_text(filepath)

    return render_template(
        "resume_result.html",
        resume_text=resume_text
    )


# ---------------- PDF REPORT ---------------- #

@app.route("/download_report")
def download_report():

    role = session.get("last_role", "Interview")
    feedback = session.get("last_feedback", "No Feedback")

    filepath = os.path.join(
        REPORT_FOLDER,
        "interview_report.pdf"
    )

    generate_report(
        role,
        feedback,
        filepath
    )

    return send_file(
        filepath,
        as_attachment=True
    )


if __name__ == "__main__":
    app.run(debug=True)
