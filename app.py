
import os
import csv
import io
import tempfile
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# --------------------------------------------------
# 1. CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

# Load API key from Streamlit Cloud Secrets or local .env
try:
    if "GROQ_API_Key" in st.secrets:
        os.environ["GROQ_API_Key"] = st.secrets["GROQ_API_Key"]
except Exception:
    pass

load_dotenv()

if not os.getenv("GROQ_API_Key"):
    st.error(
        "Groq API key not found. Configure it in your "
        "local .env file or Streamlit Cloud Secrets."
    )
    st.stop()

# Import your existing backend only after loading the key
import resume_reader as rr


# --------------------------------------------------
# 2. APPLICATION HEADER
# --------------------------------------------------

st.title("📄 AI-Powered Resume Screening System")

st.write(
    "Analyze resumes against a job description using "
    "AI-powered resume parsing and skill matching."
)

st.divider()


# --------------------------------------------------
# 3. JOB DESCRIPTION
# --------------------------------------------------

st.subheader("1. Job Description")

job_description = st.text_area(
    "Enter the job description",
    value=rr.job_description,
    height=300
)


# --------------------------------------------------
# 4. RESUME UPLOAD
# --------------------------------------------------

st.subheader("2. Upload Resumes")

uploaded_files = st.file_uploader(
    "Upload candidate resumes (PDF or DOCX)",
    type=["pdf", "docx"],
    accept_multiple_files=True
)

st.caption("You can upload multiple resumes at once.")


# --------------------------------------------------
# 5. PROCESS RESUMES
# --------------------------------------------------

if st.button(
    "Analyze Resumes",
    type="primary",
    use_container_width=True
):

    if not job_description.strip():
        st.error("Please enter a job description.")

    elif not uploaded_files:
        st.warning("Please upload at least one resume.")

    else:

        all_results = []

        try:
            with st.spinner("Analyzing job description..."):
                parsed_job = rr.parse_job_description(
                    job_description
                )

            st.success("Job description analyzed successfully!")

            progress = st.progress(0)

            for index, uploaded_file in enumerate(uploaded_files):

                st.write(
                    f"Processing {index + 1}/{len(uploaded_files)}: "
                    f"{uploaded_file.name}"
                )

                temp_path = None

                try:
                    suffix = Path(uploaded_file.name).suffix.lower()

                    # Save uploaded file temporarily
                    with tempfile.NamedTemporaryFile(
                        suffix=suffix,
                        delete=False
                    ) as temp_file:

                        temp_file.write(uploaded_file.getvalue())
                        temp_path = Path(temp_file.name)

                    # Extract resume text
                    resume_text = rr.read_resume(temp_path)

                    if not resume_text.strip():
                        raise ValueError(
                            "No extractable text found."
                        )

                    # Parse candidate information
                    parsed_resume = rr.parse_resume(resume_text)

                    # Evaluate candidate against job description
                    result = rr.final_score(
                        parsed_job,
                        parsed_resume
                    )

                    candidate = {
                        "name": parsed_resume.name or uploaded_file.name,
                        "email": parsed_resume.email or "",
                        "phone": parsed_resume.phone or "",
                        "score": result.score,
                        "verdict": result.verdict,
                        "matching_skills": result.matching_skills,
                        "missing_skills": result.missing_skills,
                        "preferred_skills_found": result.preferred_skills_found,
                        "strengths": result.strengths,
                        "concerns": result.concerns,
                        "summary": result.summary,
                        "resume_file": uploaded_file.name
                    }

                    all_results.append(candidate)

                    st.success(
                        f"Successfully analyzed {uploaded_file.name}"
                    )

                except Exception as error:
                    st.error(
                        f"Could not process {uploaded_file.name}: {error}"
                    )

                finally:
                    if temp_path and temp_path.exists():
                        temp_path.unlink()

                progress.progress(
                    (index + 1) / len(uploaded_files)
                )

            # --------------------------------------------------
            # 6. DISPLAY RESULTS
            # --------------------------------------------------

            if all_results:

                all_results.sort(
                    key=lambda item: item["score"],
                    reverse=True
                )

                st.divider()
                st.subheader("3. Candidate Analysis")

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "Successfully Analyzed",
                    len(all_results)
                )

                col2.metric(
                    "Average Score",
                    f"{sum(c['score'] for c in all_results) / len(all_results):.1f}/100"
                )

                col3.metric(
                    "Highest Score",
                    f"{all_results[0]['score']}/100"
                )

                st.subheader("Candidate Overview")

                overview = [
                    {
                        "Rank": rank,
                        "Candidate": candidate["name"],
                        "Score": candidate["score"],
                        "Verdict": candidate["verdict"]
                    }
                    for rank, candidate in enumerate(
                        all_results,
                        start=1
                    )
                ]

                st.dataframe(
                    overview,
                    use_container_width=True,
                    hide_index=True
                )

                st.caption(
                    "Scores and verdicts are AI-generated preliminary "
                    "assessments, not hiring decisions. Review the "
                    "original resumes and supporting evidence."
                )

                st.subheader("Detailed Candidate Reports")

                for rank, candidate in enumerate(
                    all_results,
                    start=1
                ):

                    with st.expander(
                        f"#{rank} - {candidate['name']} "
                        f"({candidate['score']}/100)"
                    ):

                        st.write(
                            f"**Email:** {candidate['email'] or 'Not found'}"
                        )

                        st.write(
                            f"**Phone:** {candidate['phone'] or 'Not found'}"
                        )

                        st.write(
                            f"**Verdict:** {candidate['verdict']}"
                        )

                        st.write("### Matching Skills")
                        st.write(
                            ", ".join(candidate["matching_skills"])
                            or "None"
                        )

                        st.write("### Missing Skills")
                        st.write(
                            ", ".join(candidate["missing_skills"])
                            or "None"
                        )

                        st.write("### Preferred Skills Found")
                        st.write(
                            ", ".join(
                                candidate["preferred_skills_found"]
                            ) or "None"
                        )

                        st.write("### Strengths")

                        for item in candidate["strengths"]:
                            st.write(f"- {item}")

                        st.write("### Concerns")

                        for item in candidate["concerns"]:
                            st.write(f"- {item}")

                        st.write("### AI Summary")
                        st.write(candidate["summary"])

                # --------------------------------------------------
                # 7. DOWNLOAD CSV
                # --------------------------------------------------

                output = io.StringIO()

                fieldnames = [
                    "name",
                    "email",
                    "phone",
                    "score",
                    "verdict",
                    "matching_skills",
                    "missing_skills",
                    "preferred_skills_found",
                    "strengths",
                    "concerns",
                    "summary",
                    "resume_file"
                ]

                writer = csv.DictWriter(
                    output,
                    fieldnames=fieldnames
                )

                writer.writeheader()

                for candidate in all_results:

                    row = candidate.copy()

                    for key in [
                        "matching_skills",
                        "missing_skills",
                        "preferred_skills_found",
                        "strengths",
                        "concerns"
                    ]:
                        row[key] = "; ".join(row[key])

                    writer.writerow(row)

                st.divider()

                st.download_button(
                    label="📥 Download Candidate Results (CSV)",
                    data="\ufeff" + output.getvalue(),
                    file_name="candidate_results.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            else:
                st.warning(
                    "No resumes were successfully analyzed."
                )

        except Exception as error:
            st.error(f"Application error: {error}")


# --------------------------------------------------
# 8. FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "AI Resume Analyzer | Built using Python, Streamlit, "
    "Groq and Pydantic"
)
