from flask import Flask, render_template, request
from PyPDF2 import PdfReader
import re

app = Flask(__name__)

# Skills recognized by the analyzer
SKILLS = [
    "python",
    "java",
    "c++",
    "c",
    "html",
    "css",
    "javascript",
    "sql",
    "mysql",
    "flask",
    "django",
    "machine learning",
    "artificial intelligence",
    "data analysis",
    "excel",
    "power bi",
    "communication",
    "teamwork",
    "problem solving",
    "git",
    "github",
    "react",
    "node.js",
    "php",
    "mongodb",
    "cloud computing"
]


def extract_text_from_pdf(file):
    """Extract readable text from a PDF resume."""

    reader = PdfReader(file)

    if reader.is_encrypted:
        try:
            reader.decrypt("")
        except Exception as error:
            raise ValueError(
                "This PDF is password-protected."
            ) from error

    text_parts = []

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)

    return "\n".join(text_parts)


def find_skills(text):
    """Find recognized skills using case-insensitive matching."""

    found = []

    for skill in SKILLS:
        # Match whole skill names rather than partial words.
        pattern = (
            r"(?<!\w)"
            + re.escape(skill)
            + r"(?!\w)"
        )

        if re.search(pattern, text, flags=re.IGNORECASE):
            found.append(skill)

    return found


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():

    resume = request.files.get("resume")
    job_description = request.form.get(
        "job_description", ""
    ).strip()

    # Check whether a file was uploaded.
    if not resume or not resume.filename:
        return "Please upload a PDF resume.", 400

    # Check the file extension.
    if not resume.filename.lower().endswith(".pdf"):
        return "Please upload a PDF file.", 400

    # Check the job description.
    if not job_description:
        return "Please enter a job description.", 400

    # Extract text from the PDF.
    try:
        resume_text = extract_text_from_pdf(resume)
    except ValueError as error:
        return str(error), 400
    except Exception:
        return (
            "Unable to read this PDF. "
            "Please try another PDF resume.",
            400
        )

    # Check for readable resume text.
    if not resume_text.strip():
        return (
            "No readable text was found in this PDF. "
            "Please upload a text-based PDF resume. "
            "Scanned PDFs may require OCR.",
            400
        )

    # Identify skills in both documents.
    resume_skills = set(find_skills(resume_text))
    required_skills = set(find_skills(job_description))

    # Calculate matching and missing skills.
    matched_skills = sorted(
        resume_skills.intersection(required_skills)
    )

    missing_skills = sorted(
        required_skills.difference(resume_skills)
    )

    # Calculate skill coverage percentage.
    total_required = len(required_skills)

    if total_required > 0:
        score = round(
            len(matched_skills) / total_required * 100
        )
    else:
        score = None

    return render_template(
        "result.html",
        score=score,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        total_required=total_required
    )


if __name__ == "__main__":
    app.run(debug=True)
