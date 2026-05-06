import os
import re
import pandas as pd
import streamlit as st

from PyPDF2 import PdfReader
from docx import Document

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# -----------------------------------
# PAGE CONFIG
# -----------------------------------
st.set_page_config(
    page_title="Automated Resume Screening Tool",
    page_icon="📄",
    layout="centered"
)

st.title("📄 Automated Resume Screening Tool")
st.write("AI-powered Resume Ranking System")

# -----------------------------------
# JOB DESCRIPTION INPUT
# -----------------------------------
job_description = st.text_area(
    "Enter Job Description",
    height=200
)

# -----------------------------------
# FILE UPLOAD
# -----------------------------------
uploaded_files = st.file_uploader(
    "Upload Resume Files",
    type=["pdf", "docx"],
    accept_multiple_files=True
)

# -----------------------------------
# CLEAN TEXT
# -----------------------------------
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9 ]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text

# -----------------------------------
# PDF EXTRACTION
# -----------------------------------
def extract_pdf_text(file):

    text = ""

    reader = PdfReader(file)

    for page in reader.pages:
        extracted = page.extract_text()

        if extracted:
            text += extracted

    return text

# -----------------------------------
# DOCX EXTRACTION
# -----------------------------------
def extract_docx_text(file):

    doc = Document(file)

    text = ""

    for para in doc.paragraphs:
        text += para.text

    return text

# -----------------------------------
# PROCESS BUTTON
# -----------------------------------
if st.button("Process Resumes"):

    if not job_description:
        st.warning("Please enter a job description.")

    elif not uploaded_files:
        st.warning("Please upload resumes.")

    else:

        results = []

        for file in uploaded_files:

            # Extract Text
            if file.name.endswith(".pdf"):
                resume_text = extract_pdf_text(file)

            elif file.name.endswith(".docx"):
                resume_text = extract_docx_text(file)

            else:
                continue

            cleaned_resume = clean_text(resume_text)
            cleaned_jd = clean_text(job_description)

            # TF-IDF
            documents = [cleaned_jd, cleaned_resume]

            vectorizer = TfidfVectorizer()

            tfidf_matrix = vectorizer.fit_transform(documents)

            similarity = cosine_similarity(
                tfidf_matrix[0:1],
                tfidf_matrix[1:2]
            )[0][0]

            score = round(similarity * 100, 2)

            status = (
                "Shortlisted"
                if score >= 20
                else "Rejected"
            )

            results.append({
                "Resume": file.name,
                "Score": score,
                "Status": status
            })

        # Create DataFrame
        df = pd.DataFrame(results)

        # Sort Scores
        df = df.sort_values(
            by="Score",
            ascending=False
        )

        # Display Results
        st.subheader("📊 Screening Results")

        st.dataframe(df)

        # Save CSV
        os.makedirs("outputs", exist_ok=True)

        output_path = "outputs/resume_ranking.csv"

        df.to_csv(output_path, index=False)

        st.success("CSV Report Generated Successfully!")

        # Download Button
        with open(output_path, "rb") as file:
            st.download_button(
                label="📥 Download CSV Report",
                data=file,
                file_name="resume_ranking.csv",
                mime="text/csv"
            )