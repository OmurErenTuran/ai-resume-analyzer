import os
import streamlit as st
from dotenv import load_dotenv
from pypdf import PdfReader
import google.generativeai as genai
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import io
import matplotlib.pyplot as plt


# Load API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)
st.markdown("""
<style>

/* Tüm uygulamanın arka planı */
.stApp {
    background: linear-gradient(
        135deg,
        #020617 0%,
        #0F172A 40%,
        #1E3A8A 100%
    );
    color: white;
}

/* Sayfa içeriği */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Başlıklar */
h1, h2, h3, h4 {
    color: white;
}

/* Yazılar */
p, label {
    color: #E2E8F0;
}

/* Skill badge */
.skill-badge {
    display: inline-block;
    background: #2563EB;
    color: white;
    padding: 8px 14px;
    border-radius: 20px;
    margin: 4px;
    font-size: 14px;
}
/* Job Description yazı rengi */
textarea {
    color: black !important;
    background-color: white !important;
}

/* Placeholder rengi */
textarea::placeholder {
    color: #6B7280 !important;
}
/* Analyze Resume butonu */
.stButton > button {
    background: linear-gradient(90deg, #22C55E, #16A34A);
    color: black !important;   /* Yazı siyah */
    font-weight: 700;
    border: none;
    border-radius: 12px;
    padding: 12px 20px;
    width: 100%;
}

.stButton > button:hover {
    background: linear-gradient(90deg, #16A34A, #15803D);
    color: black !important;   /* Hover'da da siyah kalsın */
}
/* Job Description Card */
.job-card{
    background: rgba(255,255,255,0.05);
    border:1px solid rgba(59,130,246,0.35);
    backdrop-filter: blur(12px);
    border-radius:20px;
    padding:22px;
    margin-bottom:20px;
}

/* Text Area */
textarea{
    background:#F8FAFC !important;
    color:#111827 !important;
    border-radius:16px !important;
    border:2px solid #2563EB !important;
    padding:18px !important;
    font-size:15px !important;
    line-height:1.6 !important;
}

textarea:focus{
    border:2px solid #3B82F6 !important;
    box-shadow:0 0 15px rgba(59,130,246,0.35) !important;
}

textarea::placeholder{
    color:#64748B !important;
    font-style:italic;
}
</style>
""", unsafe_allow_html=True)



st.title("📄 AI Resume Analyzer Pro")
st.caption("Analyze your resume against job descriptions and get actionable insights using Gemini AI.")
uploaded_file = st.file_uploader(
    "Upload your Resume (PDF only)",
    type=["pdf"]
)
st.divider()

st.markdown("""
<div class="job-card">
    <h2 style="margin-bottom:5px;">💼 Job Description Match</h2>
    <p style="color:#CBD5E1; margin-bottom:15px;">
        Paste a job description from LinkedIn, Kariyer.net or any career website.
        AI will compare it with your resume and optimize it for ATS.
    </p>
</div>
""", unsafe_allow_html=True)

job_description = st.text_area(
    "Job Description",
    height=280,
    label_visibility="collapsed",
    placeholder="""Paste a job description here...

Example:

AWS Cloud Support Engineer

Responsibilities:
• Provide technical support for AWS services.
• Troubleshoot EC2, IAM, VPC and CloudWatch issues.
• Collaborate with DevOps and Security teams.

Required Skills:
AWS • Linux • Docker • Python • GitHub • IAM
"""
)
def read_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text
SKILLS = [
    "Python","AWS","Docker","Kubernetes","Terraform",
    "Git","GitHub","Linux","SQL","JavaScript",
    "React","Node.js","CloudWatch","IAM","VPC",
    "Lambda","EC2","S3","RDS","Security Hub",
    "GuardDuty","Macie","Jenkins","CI/CD"
]

def extract_skills(text):
    found = []

    for skill in SKILLS:
        if skill.lower() in text.lower():
            found.append(skill)

    return sorted(found)


def compare_skills(resume_text, job_text):
    resume_skills = set(extract_skills(resume_text))
    job_skills = set(extract_skills(job_text))

    matched = sorted(resume_skills & job_skills)
    missing = sorted(job_skills - resume_skills)

    return matched, missing


def calculate_match_score(matched, missing):
    total = len(matched) + len(missing)

    if total == 0:
        return 0

    return round((len(matched) / total) * 100)
def create_pdf_report(analysis_text):
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    story = [Paragraph("<b>AI Resume Analysis Report</b>", styles["Heading1"])]

    for line in analysis_text.split("\n"):
        story.append(Paragraph(line, styles["BodyText"]))

    doc.build(story)

    buffer.seek(0)
    return buffer

    

if uploaded_file:

    resume_text = read_pdf(uploaded_file)

    # Dashboard verileri
    matched, missing = compare_skills(resume_text, job_description)
    score = calculate_match_score(matched, missing)
    skills = extract_skills(resume_text)

    st.success("✅ Resume uploaded successfully!")

    # ATS Dashboard
    st.subheader("🎯 ATS Match Dashboard")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("🎯 ATS Match", f"{score}%")

    with col2:
        st.metric("✅ Matched Skills", len(matched))

    with col3:
        st.metric("❌ Missing Skills", len(missing))

    st.progress(score / 100)
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
    left_space, chart_col, info_col, right_space = st.columns([0.4, 1.3, 1.1, 0.4])

    with chart_col:
        st.markdown("<div style='margin-top:50px;'></div>", unsafe_allow_html=True)
        st.subheader("📊 Skills Match Overview")

        # Grafik burada oluşturuluyor
        fig, ax = plt.subplots(figsize=(2.8, 2.8))

        sizes = [len(matched), len(missing)]
        colors = ["#22C55E", "#EF4444"]

        ax.pie(
            sizes,
            colors=colors,
            startangle=90,
            counterclock=False,
            wedgeprops=dict(width=0.30, edgecolor="white")
        )

        ax.text(0, 0.05, f"{score}%", ha="center", va="center",
                fontsize=18, fontweight="bold")
        ax.text(0, -0.18, "ATS Match", ha="center", va="center",
                fontsize=7, color="gray")

        ax.set(aspect="equal")
        ax.axis("off")

        # En son gösteriliyor
        st.pyplot(fig, use_container_width=False)
        plt.close(fig)

    with info_col:
        
        
        ax.text(
        0, -0.18,
        "ATS Match",
        ha="center",
        va="center",
        fontsize=9,
        color="black"
    )
    

    with info_col:
        st.markdown("### Skills Summary")

        match_col, miss_col = st.columns(2)

        with match_col:
            st.success(f"✅ Matched Skills: {len(matched)}")

            if matched:
                for skill in matched:
                    st.markdown(f"🟢 {skill}")
        with miss_col:
            st.error(f"❌ Missing Skills: {len(missing)}")

            if missing:
                for skill in missing:
                    st.markdown(f"🔴 {skill}")
            


# 📊 Skills Pie Chart


# 📉 Missing Skills Chart
    if missing:
        st.subheader("📉 Top Missing Skills")

        fig2, ax2 = plt.subplots(figsize=(6, 3))
        ax2.barh(missing, [1] * len(missing))
        ax2.set_xlabel("Missing from Resume")

        st.pyplot(fig2)

    if score >= 80:
        st.success("🟢 Excellent ATS Match!")
    elif score >= 60:
        st.warning("🟡 Good Match — Some improvements recommended.")
    else:
        st.error("🔴 Low Match — Add more relevant keywords.")

        # Skill badge'leri
        st.subheader("🛠️ Detected Technical Skills")

        if skills:
            badge_html = ""
            for skill in skills:
                badge_html += f'<span class="skill-badge">{skill}</span>'
            st.markdown(badge_html, unsafe_allow_html=True)
        else:
            st.info("No predefined technical skills detected.")

        # CV önizleme
        with st.expander("📄 Preview Resume Text"):
            st.write(resume_text[:3000])
        st.divider()

        st.subheader("✨ AI Resume Rewrite")

        rewrite_style = st.selectbox(
            "Choose Rewrite Style",
            [
                "ATS Optimized",
                "Professional",
                "Concise",
                "Cloud Engineer",
                "Software Engineer"
            ]
        )

        target_title = st.text_input(
            "Target Job Title",
            placeholder="Example: AWS Cloud Support Engineer"
        )
        # Analiz butonu
        
        if st.button("🪄 Rewrite Resume with AI"):

            if not job_description.strip():
                st.warning("Please paste a job description first.")
                st.stop()

            model = genai.GenerativeModel("gemini-3.6-flash")

            rewrite_prompt = f"""
        You are a senior technical recruiter and ATS resume writer.

        Rewrite the following resume specifically for this role.

        Requirements:

        - Style: {rewrite_style}
        - Target Role: {target_title}

        Rules:

        - Keep all information truthful.
        - Do not invent experience.
        - Rewrite bullet points using stronger action verbs.
        - Add ATS-friendly keywords from the job description.
        - Improve formatting and readability.
        - Optimize for recruiters and ATS systems.

        Return the rewritten resume in Markdown.

        Resume:
        {resume_text}

        Job Description:
        {job_description}
        """

        try:
            with st.spinner("Rewriting Resume..."):
                rewrite = model.generate_content(rewrite_prompt)

            st.success("✅ Resume Rewritten Successfully!")
            st.markdown("## 📄 Rewritten Resume")
            st.markdown(rewrite.text)

            rewritten_pdf = create_pdf_report(rewrite.text)

            st.download_button(
                label="⬇️ Download Rewritten Resume (PDF)",
                data=rewritten_pdf,
                file_name="Rewritten_Resume.pdf",
                mime="application/pdf"
            )

        except Exception as e:
            st.error(f"Rewrite failed: {e}")

            prompt = f"""
        You are an experienced technical recruiter.

        Analyze the resume against the provided job description.

        Return your response in English using these sections:

        # Resume Summary
        Give a short professional summary..

        # Matched Skills
        List the skills found in both the resume and the job description.

        # Missing Skills
        List important skills mentioned in the job description but missing from the resume.

        # ATS Improvement Suggestions
        Suggest keywords and improvements to increase ATS compatibility.

        # Tailored Recommendations
        Explain how the resume could be improved for this specific role.

        Resume:
        {resume_text}

        Job Description:
        {job_description}
        """

            try:
                with st.spinner("Analyzing with Gemini AI..."):
                    response = model.generate_content(prompt)

                st.success("✅ Analysis Complete!")
                st.markdown(response.text)
                pdf = create_pdf_report(response.text)

                st.download_button(
                    label="📄 Download AI Report (PDF)",
                    data=pdf,
                    file_name="AI_Resume_Report.pdf",
                    mime="application/pdf"
                )

            except Exception as e:
                st.error(f"❌ Analysis failed: {e}")