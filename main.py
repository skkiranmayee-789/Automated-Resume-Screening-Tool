import os
import re
import pandas as pd
from PyPDF2 import PdfReader
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# -----------------------------
# JOB DESCRIPTION
# -----------------------------
job_description = """
Looking for a Python Developer with skills in:
Python, SQL, Machine Learning, Data Analysis, NLP
"""

# -----------------------------
# CLEAN TEXT FUNCTION
# -----------------------------
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9 ]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text

# -----------------------------
# PDF TEXT EXTRACTION
# -----------------------------
def extract_pdf_text(pdf_path):
    text = ""
    reader = PdfReader(pdf_path)

    for page in reader.pages:
        text += page.extract_text()

    return text

# -----------------------------
# DOCX TEXT EXTRACTION
# -----------------------------
def extract_docx_text(docx_path):
    doc = Document(docx_path)

    text = ""
    for para in doc.paragraphs:
        text += para.text

    return text

# -----------------------------
# READ RESUMES
# -----------------------------
resume_folder = "resumes"

resume_data = []

for file in os.listdir(resume_folder):

    file_path = os.path.join(resume_folder, file)

    if file.endswith(".pdf"):
        text = extract_pdf_text(file_path)

    elif file.endswith(".docx"):
        text = extract_docx_text(file_path)

    else:
        continue

    cleaned_resume = clean_text(text)

    resume_data.append({
        "name": file,
        "resume_text": cleaned_resume
    })

# -----------------------------
# TF-IDF + COSINE SIMILARITY
# -----------------------------
scores = []

for resume in resume_data:

    documents = [
        clean_text(job_description),
        resume["resume_text"]
    ]

    vectorizer = TfidfVectorizer()

    tfidf_matrix = vectorizer.fit_transform(documents)

    similarity = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:2]
    )[0][0]

    percentage = round(similarity * 100, 2)

    status = "Shortlisted" if percentage >= 20 else "Rejected"

    scores.append({
        "Resume": resume["name"],
        "Score": percentage,
        "Status": status
    })

# -----------------------------
# CREATE DATAFRAME
# -----------------------------
df = pd.DataFrame(scores)

# Ranking
df = df.sort_values(by="Score", ascending=False)

# Save CSV
os.makedirs("outputs", exist_ok=True)

df.to_csv("outputs/resume_ranking.csv", index=False)

# -----------------------------
# PRINT RESULTS
# -----------------------------
print("\n===== Resume Screening Results =====\n")

print(df)

print("\nCSV report generated successfully!")