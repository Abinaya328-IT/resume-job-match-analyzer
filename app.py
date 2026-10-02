
from flask import Flask, render_template, request
from PyPDF2 import PdfReader
from docx import Document
import os
import re

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# -----------------------------
# Extract text from PDF
# -----------------------------
def extract_pdf_text(file_path):
    text = ""

    reader = PdfReader(file_path)

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


# -----------------------------
# Extract text from DOCX
# -----------------------------
def extract_docx_text(file_path):
    document = Document(file_path)

    text = ""

    for paragraph in document.paragraphs:
        text += paragraph.text + "\n"

    return text


# -----------------------------
# Extract resume text
# -----------------------------
def extract_resume_text(file_path, filename):

    extension = os.path.splitext(filename)[1].lower()

    if extension == ".pdf":
        return extract_pdf_text(file_path)

    elif extension == ".docx":
        return extract_docx_text(file_path)

    else:
        return ""


# -----------------------------
# Skills list
# -----------------------------
SKILLS = [
    "python",
    "java",
    "c++",
    "c",
    "sql",
    "html",
    "css",
    "javascript",
    "flask",
    "django",
    "machine learning",
    "data science",
    "excel",
    "ms office",
    "git",
    "github",
    "react",
    "node.js",
    "mongodb",
    "mysql"
]


# -----------------------------
# Find skills in text
# -----------------------------
def find_skills(text):

    text = text.lower()

    found_skills = []

    for skill in SKILLS:

        if skill == "c":
            pattern = r"\bc\b"

        elif skill == "c++":
            pattern = r"c\+\+"

        elif skill == "node.js":
            pattern = r"node\.js"

        else:
            pattern = r"\b" + re.escape(skill) + r"\b"

        if re.search(pattern, text):
            found_skills.append(skill)

    return found_skills


# -----------------------------
# Generate Resume Summary
# -----------------------------
def generate_summary(resume_text, matched_skills, missing_skills):

    total_skills = len(matched_skills) + len(missing_skills)

    if total_skills == 0:
        return "No relevant skills were detected."

    if len(missing_skills) == 0:
        return (
            "Your resume contains all the detected skills "
            "from the job description."
        )

    return (
        f"Your resume contains {len(matched_skills)} matching skills "
        f"out of {total_skills} detected job skills. "
        f"Consider improving: {', '.join(missing_skills)}."
    )


# -----------------------------
# ATS Rating
# -----------------------------
def get_ats_rating(score):

    if score >= 90:
        return "Excellent Match", "🟢"

    elif score >= 75:
        return "Good Match", "🟢"

    elif score >= 50:
        return "Moderate Match", "🟡"

    else:
        return "Needs Improvement", "🔴"


# -----------------------------
# Recommend Job Roles
# -----------------------------
def recommend_jobs(resume_skills):

    recommendations = []

    if "python" in resume_skills:
        recommendations.append("Python Developer")

    if "java" in resume_skills:
        recommendations.append("Java Developer")

    if "javascript" in resume_skills:
        recommendations.append("JavaScript Developer")

    if "react" in resume_skills:
        recommendations.append("Frontend Developer")

    if "html" in resume_skills and "css" in resume_skills:
        recommendations.append("Web Developer")

    if "machine learning" in resume_skills:
        recommendations.append("Machine Learning Engineer")

    if "data science" in resume_skills:
        recommendations.append("Data Scientist")

    if "sql" in resume_skills or "mysql" in resume_skills:
        recommendations.append("Database Developer")

    if "flask" in resume_skills:
        recommendations.append("Flask Developer")

    if "django" in resume_skills:
        recommendations.append("Django Developer")

    if not recommendations:
        recommendations.append("General IT / Software Developer")

    return recommendations


# -----------------------------
# Home page
# -----------------------------
@app.route("/")
def home():
    return render_template("index.html")


# -----------------------------
# Analyze Resume
# -----------------------------
@app.route("/analyze", methods=["POST"])
def analyze():

    resume = request.files.get("resume")

    job_description = request.form.get(
        "job_description",
        ""
    )

    # -----------------------------
    # Check resume
    # -----------------------------
    if not resume or resume.filename == "":
        return "Please upload a PDF or DOCX resume."

    # -----------------------------
    # Check file type
    # -----------------------------
    allowed_extensions = [
        ".pdf",
        ".docx"
    ]

    extension = os.path.splitext(
        resume.filename
    )[1].lower()

    if extension not in allowed_extensions:
        return "Only PDF and DOCX files are supported."

    # -----------------------------
    # Check job description
    # -----------------------------
    if not job_description.strip():
        return "Please enter the job description."

    # -----------------------------
    # Save resume
    # -----------------------------
    resume_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        resume.filename
    )

    resume.save(resume_path)

    # -----------------------------
    # Extract resume text
    # -----------------------------
    resume_text = extract_resume_text(
        resume_path,
        resume.filename
    )

    if not resume_text.strip():
        return "Could not extract text from the resume."

    # -----------------------------
    # Find skills
    # -----------------------------
    resume_skills = find_skills(
        resume_text
    )

    job_skills = find_skills(
        job_description
    )

    # -----------------------------
    # Matched skills
    # -----------------------------
    matched_skills = [
        skill
        for skill in job_skills
        if skill in resume_skills
    ]

    # -----------------------------
    # Missing skills
    # -----------------------------
    missing_skills = [
        skill
        for skill in job_skills
        if skill not in resume_skills
    ]

    # -----------------------------
    # Total skills
    # -----------------------------
    total_skills = len(job_skills)

    # -----------------------------
    # Calculate match score
    # -----------------------------
    if total_skills > 0:

        score = round(
            (len(matched_skills) / total_skills) * 100
        )

    else:

        score = 0

    # -----------------------------
    # Generate summary
    # -----------------------------
    summary = generate_summary(
        resume_text,
        matched_skills,
        missing_skills
    )

    # -----------------------------
    # ATS Rating
    # -----------------------------
    ats_rating, ats_icon = get_ats_rating(
        score
    )

    # -----------------------------
    # Recommend job roles
    # -----------------------------
    job_recommendations = recommend_jobs(
        resume_skills
    )

    # -----------------------------
    # Show result page
    # -----------------------------
    return render_template(
        "result.html",

        match_score=score,

        filename=resume.filename,

        matched_skills=matched_skills,

        missing_skills=missing_skills,

        total_skills=total_skills,

        recommended_roles=job_recommendations,

        summary=summary,

        ats_rating=ats_rating,

        ats_icon=ats_icon
    )


# -----------------------------
# Run Flask
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True);