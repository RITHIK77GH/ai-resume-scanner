import streamlit as st
from groq import Groq
import pdfplumber
from docx import Document
from reportlab.pdfgen import canvas
import tempfile
import os

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="AI Resume Scanner",
    page_icon="📄",
    layout="wide"
)

# -----------------------------
# GROQ CLIENT
# -----------------------------
api_key = st.secrets.get("GROQ_API_KEY")

if not api_key or api_key == "your-groq-api-key-here":
    st.error(
        "GROQ_API_KEY is missing or not set.\n"
        "Add your API key to .streamlit/secrets.toml and restart the app."
    )
    st.stop()

client = Groq(
    api_key=api_key
)

# -----------------------------
# FUNCTIONS
# -----------------------------
def extract_pdf_text(file):
    text = ""

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    return text


def extract_docx_text(file):
    doc = Document(file)

    text = "\n".join(
        para.text for para in doc.paragraphs
    )

    return text


def extract_resume(uploaded_file):
    extension = uploaded_file.name.split(".")[-1]

    if extension.lower() == "pdf":
        return extract_pdf_text(uploaded_file)

    elif extension.lower() == "docx":
        return extract_docx_text(uploaded_file)

    else:
        return ""


def analyze_resume(resume_text, job_description):

    prompt = f"""
You are an ATS Resume Analyzer.

Analyze the resume against the Job Description.

Return:

1. ATS Match Score (0-100)
2. Matching Skills
3. Missing Skills
4. Strengths
5. Weaknesses
6. Resume Improvement Suggestions
7. Final Verdict

JOB DESCRIPTION:
{job_description}

RESUME:
{resume_text}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    return response.choices[0].message.content


def generate_pdf(report):

    temp_pdf = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    )

    GROQ_API_KEY='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'

    y = 800

    for line in report.split("\n"):

        c.drawString(
            40,
            y,
            line[:100]
        )

        y -= 15

        if y < 50:
            c.showPage()
            y = 800

    c.save()

    return temp_pdf.name


# -----------------------------
# HEADER
# -----------------------------
st.title("🤖 AI Resume Scanner")
st.markdown(
    "### ATS Resume Analyzer using Groq AI"
)

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.header("Upload Files")

resume_file = st.sidebar.file_uploader(
    "Upload Resume",
    type=["pdf", "docx"]
)

job_description = st.sidebar.text_area(
    "Paste Job Description",
    height=250
)

# -----------------------------
# MAIN AREA
# -----------------------------
if resume_file:

    st.success("Resume Uploaded Successfully")

    resume_text = extract_resume(
        resume_file
    )

    with st.expander("Resume Preview"):
        st.write(
            resume_text[:5000]
        )

    if st.button("Analyze Resume"):

        if job_description.strip() == "":
            st.warning(
                "Please enter Job Description"
            )

        else:

            with st.spinner(
                "Analyzing Resume..."
            ):

                result = analyze_resume(
                    resume_text,
                    job_description
                )

            st.subheader(
                "Analysis Result"
            )

            st.markdown(result)

            pdf_path = generate_pdf(
                result
            )

            with open(
                pdf_path,
                "rb"
            ) as f:

                st.download_button(
                    label="📥 Download Report",
                    data=f,
                    file_name="Resume_Analysis_Report.pdf",
                    mime="application/pdf"
                )

            os.remove(pdf_path)

else:
    st.info(
        "Upload your resume to start analysis."
    )

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("---")
st.caption(
    "Built with Streamlit + Groq AI"
)