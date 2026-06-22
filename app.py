"""
AI-powered Resume Parser with Skill Gap Analyzer
Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd

from src.file_reader import read_resume
from src.job_matcher import compare_with_job
from src.resume_parser import parse_resume
from src.utils import build_export_payload, match_score_css, to_pretty_json

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Resume Parser | Skill Gap Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main-title { font-size: 2.2rem; font-weight: 800; margin-bottom: 0.2rem; }
    .sub-title { color: #64748b; margin-bottom: 1.5rem; }
    .metric-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1rem;
        min-height: 90px;
    }
    .gap-pill {
        display: inline-block;
        background: #fee2e2;
        color: #b91c1c;
        padding: 0.25rem 0.6rem;
        border-radius: 999px;
        margin: 0.15rem;
        font-size: 0.85rem;
    }
    .match-pill {
        display: inline-block;
        background: #dcfce7;
        color: #166534;
        padding: 0.25rem 0.6rem;
        border-radius: 999px;
        margin: 0.15rem;
        font-size: 0.85rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("How it works")
    st.markdown(
        """
        1. **Upload** your resume (PDF or DOCX)
        2. We extract contact info, skills, education, and more
        3. **Paste** a job description to get a match score
        4. See **skill gaps** and download JSON results

        **Hinglish support:** Recognizes abbreviations like ML, AI, DS and
        common Indian student resume phrases.
        """
    )
    st.divider()
    st.caption("Built with Python · spaCy · Streamlit · PyMuPDF")

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown('<p class="main-title">📄 AI Resume Parser</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-title">Extract resume data and compare it with any job description.</p>',
    unsafe_allow_html=True,
)

col_upload, col_jd = st.columns([1, 1], gap="large")

# ---------------------------------------------------------------------------
# Upload + Job Description inputs
# ---------------------------------------------------------------------------
with col_upload:
    st.subheader("1. Upload Resume")
    uploaded_file = st.file_uploader(
        "PDF or DOCX",
        type=["pdf", "docx"],
        help="Upload your resume file. Max recommended size: 5 MB.",
    )

with col_jd:
    st.subheader("2. Paste Job Description")
    job_description = st.text_area(
        "Job Description",
        height=220,
        placeholder="Paste the full job description here...\n\nExample: Looking for a Python developer with ML, SQL, and Docker experience...",
        label_visibility="collapsed",
    )

analyze_clicked = st.button("Analyze Resume & Match Skills", type="primary", use_container_width=True)

# ---------------------------------------------------------------------------
# Processing
# ---------------------------------------------------------------------------
if analyze_clicked:
    if not uploaded_file:
        st.error("Please upload a resume file first.")
        st.stop()

    with st.spinner("Reading and parsing your resume..."):
        try:
            raw_text = read_resume(uploaded_file.getvalue(), uploaded_file.name)
            parsed = parse_resume(raw_text)
        except Exception as exc:
            st.error(f"Could not read resume: {exc}")
            st.stop()

    st.session_state["parsed_resume"] = parsed
    st.session_state["raw_text"] = raw_text

    if job_description.strip():
        match = compare_with_job(parsed["skills"], job_description)
        st.session_state["match_result"] = {
            "match_score": match.match_score,
            "score_label": match.score_label,
            "score_color": match.score_color,
            "matched_skills": match.matched_skills,
            "skill_gaps": match.skill_gaps,
            "job_skills_detected": match.job_skills,
        }
    else:
        st.session_state["match_result"] = None
        st.info("No job description provided — showing parsed resume only.")

# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
if "parsed_resume" in st.session_state:
    parsed = st.session_state["parsed_resume"]
    match_result = st.session_state.get("match_result")

    st.divider()
    st.subheader("Results Dashboard")

    # Match score banner
    if match_result:
        st.markdown("#### Job Match Score")
        st.markdown(
            f'<div style="{match_score_css(match_result["score_color"])}">'
            f'{match_result["match_score"]}% — {match_result["score_label"]}'
            f"</div>",
            unsafe_allow_html=True,
        )

        m1, m2, m3 = st.columns(3)
        m1.metric("Skills in Job", len(match_result["job_skills_detected"]))
        m2.metric("Matched Skills", len(match_result["matched_skills"]))
        m3.metric("Skill Gaps", len(match_result["skill_gaps"]))

    # Contact + overview
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Name", parsed.get("name") or "Not found")
    c2.metric("Email", parsed.get("email") or "Not found")
    c3.metric("Phone", parsed.get("phone") or "Not found")
    c4.metric("Skills Found", len(parsed.get("skills", [])))

    tab_skills, tab_edu, tab_exp, tab_cert, tab_gaps, tab_raw = st.tabs(
        ["Skills", "Education", "Experience", "Certifications", "Skill Gaps", "Raw Preview"]
    )

    with tab_skills:
        skills = parsed.get("skills", [])
        if skills:
            st.markdown(" ".join(f'<span class="match-pill">{s}</span>' for s in skills), unsafe_allow_html=True)
            st.dataframe(pd.DataFrame({"Skill": skills}), use_container_width=True, hide_index=True)
        else:
            st.warning("No skills detected. Try adding a Skills section with keywords like Python, ML, SQL.")

    with tab_edu:
        education = parsed.get("education", [])
        if education:
            for item in education:
                st.markdown(f"- {item}")
        else:
            st.info("No education entries detected.")

    with tab_exp:
        experience = parsed.get("experience", [])
        if experience:
            for item in experience:
                st.markdown(f"- {item}")
        else:
            st.info("No experience entries detected. Add dates like 2023 - 2024 for better extraction.")

    with tab_cert:
        certs = parsed.get("certifications", [])
        if certs:
            for item in certs:
                st.markdown(f"- {item}")
        else:
            st.info("No certifications detected.")

    with tab_gaps:
        if match_result:
            matched = match_result.get("matched_skills", [])
            gaps = match_result.get("skill_gaps", [])

            st.markdown("**Matched skills** (you have these)")
            if matched:
                st.markdown(" ".join(f'<span class="match-pill">{s}</span>' for s in matched), unsafe_allow_html=True)
            else:
                st.warning("No overlapping skills found.")

            st.markdown("**Skill gaps** (consider learning these)")
            if gaps:
                st.markdown(" ".join(f'<span class="gap-pill">{s}</span>' for s in gaps), unsafe_allow_html=True)
            else:
                st.success("Great! No skill gaps detected for this job.")
        else:
            st.info("Paste a job description and click Analyze to see skill gaps.")

    with tab_raw:
        st.text_area("Extracted text preview", parsed.get("raw_text_preview", ""), height=300)

    # JSON download
    st.divider()
    export_data = build_export_payload(parsed, match_result)
    st.download_button(
        label="Download Parsed Resume (JSON)",
        data=to_pretty_json(export_data),
        file_name="parsed_resume.json",
        mime="application/json",
        use_container_width=True,
    )

else:
    st.info("Upload a resume and click **Analyze Resume & Match Skills** to see results.")

    with st.expander("Sample job description (copy & paste to test)"):
        st.code(
            """
We are hiring a Junior Data Scientist.

Requirements:
- Strong Python and SQL skills
- Experience with Machine Learning (ML) and Data Science projects
- Knowledge of pandas, numpy, and scikit-learn
- Familiarity with Git, Docker, and REST APIs
- Good communication and problem-solving skills

Nice to have: Deep Learning, AWS, Power BI
            """.strip(),
            language="text",
        )
