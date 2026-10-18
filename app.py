from flask import Flask, render_template, request
from PyPDF2 import PdfReader
from collections import Counter
import re

app = Flask(__name__)

# Skills that our analyzer can recognize
SKILLS = [
    "python", "java", "c++", "c", "html", "css",
    "javascript", "sql", "mysql", "flask", "django",
    "machine learning", "artificial intelligence",
    "data analysis", "excel", "power bi",
    "communication", "teamwork", "problem solving",
    "git", "github", "react", "node.js",
    "php", "mongodb", "cloud computing"
]


def extract_text_from_pdf(file):
    """Extract text from an uploaded PDF resume."""
    reader = PdfReader(file)
    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    return text


def find_skills(text):
    """Find known skills in text."""
    text = text.lower()
    found = []

    for skill in SKILLS:
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

        if re.search(pattern, text):
            found.append(skill.title())

    return found


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    resume = request.files.get("resume")
    job_description = request.form.get("job_description", "").strip()

    if not resume or not resume.filename:
        return "Please upload a PDF resume.", 400

    if not resume.filename.lower().endswith(".pdf"):
        return "Please upload a PDF file.", 400

    if not job_description:
        return "Please enter a job description.", 400

    try:
        resume_text = extract_text_from_pdf(resume)
    except Exception:
        return "Unable to read this PDF. Please try another PDF resume.", 400

    if not resume_text.strip():
        return (
            "No readable text found. Please use a text-based PDF resume.",
            400
        )

    resume_skills = set(find_skills(resume_text))
    required_skills = set(find_skills(job_description))

    matched_skills = sorted(resume_skills & required_skills)
    missing_skills = sorted(required_skills - resume_skills)

    if required_skills:
        score = round(
            len(matched_skills) / len(required_skills) * 100
        )
    else:
        score = 0

    return render_template(
        "result.html",
        score=score,
        matched_skills=matched_skills,
        missing_skills=missing_skills
    )


if __name__ == "__main__":
    app.run(debug=True)