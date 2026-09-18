
import streamlit as st
import pandas as pd
import plotly.express as px
import re

# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="CareerMatch",
    page_icon="🎯",
    layout="wide"
)

# =====================================================
# SKILL DATABASE
# =====================================================

SKILL_DATABASE = {
    "Programming": [
        "python", "java", "javascript", "c++", "c#", "php",
        "typescript", "kotlin", "swift", "ruby", "go"
    ],
    "Web Development": [
        "html", "css", "react", "angular", "vue",
        "node.js", "laravel", "django", "flask",
        "bootstrap", "tailwind"
    ],
    "Database": [
        "mysql", "postgresql", "sql", "mongodb",
        "sqlite", "oracle", "redis", "firebase"
    ],
    "Tools": [
        "git", "github", "docker", "kubernetes",
        "linux", "jira", "figma", "postman"
    ],
    "Data and AI": [
        "machine learning", "deep learning", "nlp",
        "natural language processing", "pandas",
        "numpy", "tensorflow", "pytorch",
        "data analysis", "data visualization"
    ],
    "Cloud": [
        "aws", "azure", "google cloud", "gcp",
        "cloud computing"
    ],
    "Soft Skills": [
        "communication", "teamwork", "leadership",
        "problem solving", "critical thinking",
        "time management", "adaptability"
    ]
}

# =====================================================
# HELPER FUNCTIONS
# =====================================================

def normalize_text(text):
    """Convert text to lowercase for comparison."""
    return text.lower()


def extract_skills(text):
    """
    Detect skills from text using a predefined
    skill dictionary.
    """
    text = normalize_text(text)
    found_skills = {}

    for category, skills in SKILL_DATABASE.items():
        found_skills[category] = []

        for skill in skills:
            # Escape special characters for safe matching
            pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

            if re.search(pattern, text):
                found_skills[category].append(skill)

    return found_skills


def flatten_skills(skill_dictionary):
    """Convert categorized skills into one list."""
    all_skills = []

    for skills in skill_dictionary.values():
        all_skills.extend(skills)

    return sorted(set(all_skills))


def compare_skills(resume_skills, job_skills):
    """
    Compare detected resume skills with
    detected job-description skills.
    """
    resume_set = set(resume_skills)
    job_set = set(job_skills)

    matching = sorted(resume_set.intersection(job_set))
    missing = sorted(job_set - resume_set)
    additional = sorted(resume_set - job_set)

    return matching, missing, additional


def create_skill_rows(resume_skills, job_skills):
    """
    Create a table showing how each detected
    job skill relates to the resume.
    """
    resume_set = set(resume_skills)
    rows = []

    for skill in sorted(set(job_skills)):
        if skill in resume_set:
            status = "Matching"
        else:
            status = "Not detected in resume"

        rows.append({
            "Required Skill": skill.title(),
            "Status": status
        })

    return pd.DataFrame(rows)


# =====================================================
# HEADER
# =====================================================

st.title("🎯 CareerMatch")
st.subheader("GenAI-Powered Resume Analysis and Job Matching Dashboard")

st.write(
    "Analyze a resume, compare it with a job description, "
    "and explore detected skills through an interactive dashboard."
)

st.info(
    "This prototype compares information detected in the documents. "
    "A skill marked as missing may simply not be mentioned in the resume."
)

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.header("📂 Input Settings")

resume_file = st.sidebar.file_uploader(
    "Upload Resume (TXT)",
    type=["txt"]
)

# =====================================================
# INPUT SECTION
# =====================================================

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📄 Resume")

    default_resume = """John Doe

Skills:
Python, Java, MySQL, HTML, CSS, Git, Laravel

Experience:
Developed web applications and managed databases.
Worked with a team on software projects.

Education:
Bachelor of Science in Information Technology
"""

    if resume_file is not None:
        resume_text = resume_file.read().decode("utf-8")
    else:
        resume_text = st.text_area(
            "Paste your resume text here",
            value=default_resume,
            height=300
        )

with col2:
    st.markdown("### 💼 Job Description")

    default_job = """We are looking for a Junior Software Developer.

Requirements:
- Knowledge of Python
- Experience with SQL
- Familiarity with Git
- Experience with REST API
- Knowledge of Docker
- Good communication skills
- Problem solving skills
"""

    job_text = st.text_area(
        "Paste the job description here",
        value=default_job,
        height=300
    )

# =====================================================
# ANALYZE BUTTON
# =====================================================

analyze_button = st.button(
    "🔍 Analyze Resume and Job",
    type="primary",
    use_container_width=True
)

if analyze_button:

    if not resume_text.strip() or not job_text.strip():
        st.error("Please provide both a resume and a job description.")
        st.stop()

    # -------------------------------------------------
    # EXTRACT SKILLS
    # -------------------------------------------------

    resume_skill_categories = extract_skills(resume_text)
    job_skill_categories = extract_skills(job_text)

    resume_skills = flatten_skills(resume_skill_categories)
    job_skills = flatten_skills(job_skill_categories)

    matching_skills, missing_skills, additional_skills = compare_skills(
        resume_skills,
        job_skills
    )

    # -------------------------------------------------
    # DASHBOARD METRICS
    # -------------------------------------------------

    st.divider()
    st.header("📊 Analysis Dashboard")

    total_required = len(job_skills)
    total_matching = len(matching_skills)
    total_missing = len(missing_skills)

    if total_required > 0:
        coverage = (total_matching / total_required) * 100
    else:
        coverage = 0

    metric1, metric2, metric3, metric4 = st.columns(4)

    metric1.metric(
        "Resume Skills",
        len(resume_skills)
    )

    metric2.metric(
        "Required Skills",
        total_required
    )

    metric3.metric(
        "Matching Skills",
        total_matching
    )

    metric4.metric(
        "Skill Coverage",
        f"{coverage:.1f}%"
    )

    # -------------------------------------------------
    # SKILL COMPARISON
    # -------------------------------------------------

    st.subheader("🔎 Skill Comparison")

    comparison_col1, comparison_col2 = st.columns(2)

    with comparison_col1:
        st.markdown("#### ✅ Matching Skills")

        if matching_skills:
            for skill in matching_skills:
                st.success(skill.title())
        else:
            st.write("No matching skills detected.")

    with comparison_col2:
        st.markdown("#### ⚠️ Skills Not Detected")

        if missing_skills:
            for skill in missing_skills:
                st.warning(skill.title())
        else:
            st.success("All detected job-description skills are present.")

    # -------------------------------------------------
    # CATEGORY ANALYSIS
    # -------------------------------------------------

    st.divider()
    st.subheader("📈 Skills by Category")

    category_rows = []

    for category in SKILL_DATABASE:
        resume_count = len(resume_skill_categories[category])
        job_count = len(job_skill_categories[category])
        matching_count = len(
            set(resume_skill_categories[category])
            .intersection(set(job_skill_categories[category]))
        )

        category_rows.append({
            "Category": category,
            "Resume Skills": resume_count,
            "Job Requirements": job_count,
            "Matching Skills": matching_count
        })

    category_df = pd.DataFrame(category_rows)

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        fig = px.bar(
            category_df,
            x="Category",
            y=["Resume Skills", "Job Requirements"],
            barmode="group",
            title="Resume vs Job Requirements"
        )

        fig.update_layout(
            xaxis_title="Skill Category",
            yaxis_title="Number of Skills",
            legend_title="Data"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with chart_col2:
        matching_category_df = category_df[
            category_df["Job Requirements"] > 0
        ]

        fig2 = px.bar(
            matching_category_df,
            x="Category",
            y="Matching Skills",
            title="Matching Skills by Category"
        )

        fig2.update_layout(
            xaxis_title="Skill Category",
            yaxis_title="Matching Skills"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

    # -------------------------------------------------
    # DETAILED COMPARISON TABLE
    # -------------------------------------------------

    st.divider()
    st.subheader("📋 Detailed Job Requirement Analysis")

    comparison_df = create_skill_rows(
        resume_skills,
        job_skills
    )

    if not comparison_df.empty:
        st.dataframe(
            comparison_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info(
            "No recognized skills were detected in the job description."
        )

    # -------------------------------------------------
    # ADDITIONAL RESUME SKILLS
    # -------------------------------------------------

    st.subheader("➕ Additional Resume Skills")

    if additional_skills:
        st.write(
            "These skills were detected in the resume but "
            "were not detected in the job description:"
        )

        st.write(", ".join(
            skill.title() for skill in additional_skills
        ))
    else:
        st.write("No additional skills detected.")

    # -------------------------------------------------
    # BASIC INSIGHTS
    # -------------------------------------------------

    st.divider()
    st.subheader("💡 CareerMatch Insights")

    if coverage >= 75:
        st.success(
            "Many of the job-description skills were detected "
            "in the resume. Review the detailed comparison for context."
        )
    elif coverage >= 40:
        st.info(
            "Some relevant skills were detected. Review the "
            "skills not detected and check whether they are "
            "present but described differently in your resume."
        )
    else:
        st.warning(
            "Few of the listed job-description skills were detected. "
            "Consider reviewing the job requirements and your resume."
        )

    # -------------------------------------------------
    # EXPORT RESULTS
    # -------------------------------------------------

    st.divider()
    st.subheader("📥 Export Analysis")

    export_df = comparison_df.copy()

    csv_data = export_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Skill Analysis CSV",
        data=csv_data,
        file_name="careermatch_skill_analysis.csv",
        mime="text/csv"
    )

else:
    st.divider()
    st.subheader("🚀 How to Use CareerMatch")

    st.write("1. Upload a TXT resume or use the sample resume.")
    st.write("2. Paste a job description.")
    st.write("3. Click **Analyze Resume and Job**.")
    st.write("4. Explore matching skills, skill gaps, and charts.")