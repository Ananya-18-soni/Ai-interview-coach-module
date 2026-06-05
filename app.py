from flask import Flask, render_template, request, redirect, session, flash, send_file
import sqlite3
import os

from utils.ai_helper import generate_questions, evaluate_answer
from utils.resume_parser import extract_resume_text
from utils.pdf_report import generate_report

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "interviewcoach")

BASE_DIR = os.path.dirname(os.path.abspath(**file**))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
REPORT_FOLDER = os.path.join(BASE_DIR, "reports")

DB_PATH = "/tmp/interview.db"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

# ---------------- DATABASE ----------------

def get_db():
conn = sqlite3.connect(DB_PATH)
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

# ---------------- HOME ---------------- #

@app.route("/")
def home():
    try:
        return render_template("login.html")
    except Exception as e:
        return f"Error loading template: {str(e)}", 500


# ---------------- REGISTER ---------------- #

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


# ---------------- LOGIN ---------------- #

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

    return render_template(
        "dashboard.html",
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

    session["feedback"] = feedback

    return render_template(
        "result.html",
        feedback=feedback
    )


# ---------------- RESUME ---------------- #

@app.route("/upload_resume", methods=["POST"])
def upload_resume():

    resume = request.files["resume"]

    path = os.path.join(
        UPLOAD_FOLDER,
        resume.filename
    )

    resume.save(path)

    resume_text = extract_resume_text(path)

    return render_template(
        "resume_result.html",
        resume_text=resume_text
    )


# ---------------- PDF ---------------- #

@app.route("/download_report")
def download_report():

    filepath = os.path.join(
        REPORT_FOLDER,
        "report.pdf"
    )

    generate_report(
        "Interview Report",
        session.get("feedback", ""),
        filepath
    )

    return send_file(
        filepath,
        as_attachment=True
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
