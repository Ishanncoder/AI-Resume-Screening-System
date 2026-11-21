import os
import csv
import io
import html
import tempfile
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

AUTHOR = "Ishan Gupta"

# --------------------------------------------------
# 1. CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AI Resume Analyzer | " + AUTHOR,
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

try:
    if "GROQ_API_Key" in st.secrets:
        os.environ["GROQ_API_Key"] = st.secrets["GROQ_API_Key"]
except Exception:
    pass

load_dotenv()

# --------------------------------------------------
# 2. FANCY THEME
# --------------------------------------------------

st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"], .stApp {font-family: 'Poppins', sans-serif;}
    #MainMenu, footer, header {visibility: hidden;}

    .stApp {
        background:
            radial-gradient(circle at 15% 10%, rgba(124,58,237,.35), transparent 40%),
            radial-gradient(circle at 85% 20%, rgba(236,72,153,.28), transparent 40%),
            radial-gradient(circle at 50% 95%, rgba(6,182,212,.22), transparent 45%),
            #0b0f1e;
        color: #e5e7eb;
    }
    .block-container {padding-top: 1.5rem; max-width: 1250px;}
    h1, h2, h3, h4, label, p, span, div {color: #e5e7eb;}

    section[data-testid="stSidebar"] {
        background: rgba(15,20,40,.85);
        border-right: 1px solid rgba(255,255,255,.08);
    }

    .hero {
        position: relative; overflow: hidden;
        background: linear-gradient(120deg, #6d28d9, #db2777, #0891b2, #6d28d9);
        background-size: 300% 300%;
        animation: shift 10s ease infinite;
        border-radius: 24px; padding: 2.6rem 2.8rem; margin-bottom: 1.6rem;
        box-shadow: 0 20px 60px rgba(124,58,237,.35);
    }
    @keyframes shift {0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%}}
    .hero h1 {margin: 0; font-size: 2.6rem; font-weight: 800; color: #fff;}
    .hero p {margin: .6rem 0 0; font-size: 1.1rem; color: rgba(255,255,255,.92);}
    .hero .by {
        display: inline-block; margin-top: 1.1rem; padding: .4rem 1rem;
        background: rgba(255,255,255,.18); border: 1px solid rgba(255,255,255,.35);
        border-radius: 999px; font-weight: 600; color: #fff; backdrop-filter: blur(6px);
    }

    .glass {
        background: rgba(255,255,255,.06);
        border: 1px solid rgba(255,255,255,.12);
        border-radius: 20px; padding: 1.2rem 1.4rem;
        backdrop-filter: blur(10px);
    }
    .step {
        display: inline-block; font-size: .72rem; font-weight: 700; letter-spacing: .12em;
        text-transform: uppercase; padding: .2rem .7rem; border-radius: 999px;
        background: linear-gradient(90deg, #7c3aed, #db2777); color: #fff; margin-bottom: .4rem;
    }

    .stat {
        background: rgba(255,255,255,.07); border: 1px solid rgba(255,255,255,.14);
        border-radius: 18px; padding: 1.1rem 1.3rem; text-align: center;
        transition: transform .2s ease, border-color .2s ease;
    }
    .stat:hover {transform: translateY(-4px); border-color: #a78bfa;}
    .stat .icon {font-size: 1.5rem;}
    .stat .label {font-size: .72rem; letter-spacing: .1em; text-transform: uppercase; color: #9ca3af;}
    .stat .value {font-size: 2rem; font-weight: 800;
        background: linear-gradient(90deg, #a78bfa, #f472b6); -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;}

    .cand {
        display: flex; align-items: center; gap: 1.2rem;
        background: rgba(255,255,255,.06); border: 1px solid rgba(255,255,255,.12);
        border-radius: 20px; padding: 1rem 1.3rem; margin-top: .9rem;
        transition: transform .2s ease, box-shadow .2s ease;
    }
    .cand:hover {transform: translateY(-3px); box-shadow: 0 12px 30px rgba(0,0,0,.35);}
    .ring {
        --p: 0; --c: #22c55e;
        width: 74px; height: 74px; border-radius: 50%; flex: none;
        background: conic-gradient(var(--c) calc(var(--p) * 1%), rgba(255,255,255,.12) 0);
        display: flex; align-items: center; justify-content: center;
    }
    .ring span {
        width: 58px; height: 58px; border-radius: 50%; background: #0f1428;
        display: flex; align-items: center; justify-content: center;
        font-weight: 800; font-size: 1.05rem; color: #fff;
    }
    .cand .name {font-size: 1.2rem; font-weight: 700; color: #fff;}
    .cand .sub {font-size: .85rem; color: #9ca3af;}
    .medal {font-size: 1.8rem; width: 2.2rem; text-align: center; flex: none;}
    .verdict {
        margin-left: auto; padding: .35rem .9rem; border-radius: 999px;
        font-size: .8rem; font-weight: 700; color: #fff; white-space: nowrap;
    }

    .chip {display:inline-block; padding:.2rem .75rem; margin:.15rem .25rem .15rem 0;
        border-radius:999px; font-size:.8rem; font-weight:500;}
    .chip-good {background: rgba(34,197,94,.18); color:#86efac; border:1px solid rgba(34,197,94,.4);}
    .chip-bad {background: rgba(239,68,68,.18); color:#fca5a5; border:1px solid rgba(239,68,68,.4);}
    .chip-pref {background: rgba(99,102,241,.2); color:#c7d2fe; border:1px solid rgba(99,102,241,.45);}
    .chip-none {color:#6b7280; font-size:.85rem;}

    .stButton > button, .stDownloadButton > button {
        border-radius: 14px; font-weight: 700; padding: .75rem 1rem;
        border: 1px solid rgba(255,255,255,.2); transition: all .2s ease;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #7c3aed, #db2777); color: #fff; border: none;
        box-shadow: 0 10px 30px rgba(219,39,119,.35);
    }
    .stDownloadButton > button {
        background: linear-gradient(90deg, #059669, #0891b2); color: #fff; border: none;
        box-shadow: 0 10px 30px rgba(8,145,178,.3);
    }
    .stButton > button:hover, .stDownloadButton > button:hover {transform: translateY(-2px); filter: brightness(1.1);}

    .stTextArea textarea, .stTextInput input {
        background: #151a35 !important; color: #f3f4f6 !important;
        -webkit-text-fill-color: #f3f4f6 !important;
        border: 1px solid rgba(255,255,255,.15) !important; border-radius: 14px !important;
    }
    .stTextArea textarea::placeholder, .stTextInput input::placeholder {
        color: #6b7280 !important; -webkit-text-fill-color: #6b7280 !important;
    }

    /* Keep every widget dark and readable, even when the phone is in light mode */
    [data-testid="stFileUploaderDropzone"] *, [data-testid="stFileUploader"] small,
    [data-testid="stFileUploader"] span {color: #e5e7eb !important;}
    [data-testid="stFileUploaderFile"], [data-testid="stFileUploaderFileData"] {
        background: #151a35 !important; border-radius: 12px;
    }
    [data-testid="stFileUploaderFileName"] {color: #f3f4f6 !important;}
    [data-testid="stStatusWidget"], [data-testid="stExpander"] details,
    [data-testid="stExpander"] summary {
        background: #151a35 !important; color: #e5e7eb !important;
    }
    [data-testid="stStatus"], [data-testid="stStatus"] * {color: #e5e7eb !important;}
    [data-testid="stStatus"] details {background: #151a35 !important; border-radius: 14px;
        border: 1px solid rgba(255,255,255,.12) !important;}
    [data-testid="stAlert"] {border-radius: 14px;}
    [data-testid="stAlertContainer"] {background: #151a35 !important;
        border: 1px solid rgba(255,255,255,.14);}
    [data-testid="stAlertContainer"] * {color: #e5e7eb !important;}
    [data-testid="stTabs"] button {color: #e5e7eb !important;}
    [data-testid="stDataFrame"] {border-radius: 14px; overflow: hidden;}
    [data-testid="stFileUploaderDropzone"] {
        background: rgba(255,255,255,.05); border: 2px dashed rgba(167,139,250,.6); border-radius: 18px;
    }
    .streamlit-expanderHeader, [data-testid="stExpander"] {
        border-radius: 14px; border: 1px solid rgba(255,255,255,.1);
    }
    .footer {text-align:center; color:#9ca3af; padding: 1.5rem 0 .5rem;}
    .footer b {background: linear-gradient(90deg,#a78bfa,#f472b6); -webkit-background-clip:text;
        -webkit-text-fill-color: transparent;}
</style>
""",
    unsafe_allow_html=True,
)

# --------------------------------------------------
# 3. API KEY CHECK + BACKEND
# --------------------------------------------------

if not os.getenv("GROQ_API_Key"):
    st.error(
        "Groq API key not found. Configure it in your "
        "local .env file or Streamlit Cloud Secrets."
    )
    st.stop()

import resume_reader as rr  # noqa: E402


# --------------------------------------------------
# 4. HELPERS
# --------------------------------------------------

LIST_KEYS = [
    "matching_skills", "missing_skills", "preferred_skills_found",
    "strengths", "concerns",
]
FIELDS = [
    "name", "email", "phone", "score", "verdict",
    "matching_skills", "missing_skills", "preferred_skills_found",
    "strengths", "concerns", "summary", "resume_file",
]


def score_color(score):
    if score >= 75:
        return "#22c55e"
    if score >= 50:
        return "#f59e0b"
    return "#ef4444"


def chips(items, css_class):
    if not items:
        return '<span class="chip-none">None</span>'
    return "".join(
        f'<span class="chip {css_class}">{html.escape(str(i))}</span>'
        for i in items
    )


def stat(icon, label, value):
    return (
        f'<div class="stat"><div class="icon">{icon}</div>'
        f'<div class="value">{value}</div><div class="label">{label}</div></div>'
    )


def flat_row(candidate):
    row = {k: candidate[k] for k in FIELDS}
    for key in LIST_KEYS:
        row[key] = "; ".join(row[key])
    return row


def build_csv(results):
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=FIELDS)
    writer.writeheader()
    for candidate in results:
        writer.writerow(flat_row(candidate))
    return ("\ufeff" + output.getvalue()).encode("utf-8")


def analyze(job_description, uploaded_files):
    results, errors = [], []

    with st.status("Analyzing resumes...", expanded=True) as status:
        st.write("Analyzing job description...")
        parsed_job = rr.parse_job_description(job_description)

        progress = st.progress(0.0)
        total = len(uploaded_files)

        for index, uploaded_file in enumerate(uploaded_files):
            st.write(f"Processing {index + 1}/{total}: {uploaded_file.name}")
            temp_path = None
            try:
                suffix = Path(uploaded_file.name).suffix.lower()
                with tempfile.NamedTemporaryFile(
                    suffix=suffix, delete=False
                ) as temp_file:
                    temp_file.write(uploaded_file.getvalue())
                    temp_path = Path(temp_file.name)

                resume_text = rr.read_resume(temp_path)
                if not resume_text.strip():
                    raise ValueError("No extractable text found.")

                parsed_resume = rr.parse_resume(resume_text)
                result = rr.final_score(parsed_job, parsed_resume)

                results.append({
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
                    "resume_file": uploaded_file.name,
                })
            except Exception as error:
                errors.append(f"{uploaded_file.name}: {error}")
            finally:
                if temp_path and temp_path.exists():
                    temp_path.unlink()

            progress.progress((index + 1) / total)

        status.update(
            label=f"Done: {len(results)} analyzed, {len(errors)} failed",
            state="complete" if results else "error",
            expanded=False,
        )

    results.sort(key=lambda c: c["score"], reverse=True)
    return results, errors


# --------------------------------------------------
# 5. SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.markdown(
        f"""
<div class="glass" style="text-align:center;">
  <div style="font-size:2.4rem;">🚀</div>
  <div style="font-weight:800; font-size:1.1rem;">Resume Analyzer</div>
  <div style="color:#9ca3af; font-size:.85rem; margin-top:.3rem;">Created by</div>
  <div style="font-weight:700; font-size:1.05rem; background:linear-gradient(90deg,#a78bfa,#f472b6);
       -webkit-background-clip:text; -webkit-text-fill-color:transparent;">{AUTHOR}</div>
</div>
""",
        unsafe_allow_html=True,
    )
    st.write("")
    st.markdown("**How it works**")
    st.markdown("1. Paste the job description\n2. Upload resumes\n3. Get ranked results\n4. Download the CSV")
    st.divider()
    st.caption(
        "Scores are AI-generated preliminary assessments, not hiring "
        "decisions. Always review the original resumes."
    )
    if st.session_state.get("results") is not None:
        if st.button("🔄 Start over", use_container_width=True):
            st.session_state.pop("results", None)
            st.session_state.pop("errors", None)
            st.rerun()

# --------------------------------------------------
# 6. HERO
# --------------------------------------------------

st.markdown(
    f"""
<div class="hero">
  <h1>🚀 AI Resume Screening</h1>
  <p>Rank candidates against your job description in seconds, with skill gaps,
  strengths and a smart summary for every resume.</p>
  <span class="by">✨ Built by {AUTHOR}</span>
</div>
""",
    unsafe_allow_html=True,
)

# --------------------------------------------------
# 7. INPUTS
# --------------------------------------------------

left, right = st.columns([3, 2], gap="large")

with left:
    st.markdown('<span class="step">Step 1</span>', unsafe_allow_html=True)
    st.subheader("Job description")
    job_description = st.text_area(
        "Job description",
        value=rr.job_description,
        height=320,
        label_visibility="collapsed",
        placeholder="Paste the job description here...",
    )

with right:
    st.markdown('<span class="step">Step 2</span>', unsafe_allow_html=True)
    st.subheader("Upload resumes")
    uploaded_files = st.file_uploader(
        "Upload candidate resumes",
        type=["pdf", "docx"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )
    if uploaded_files:
        st.success(f"{len(uploaded_files)} resume(s) ready")
    else:
        st.caption("Drag and drop PDF or DOCX files above.")

    analyze_clicked = st.button(
        "✨ Analyze Resumes", type="primary", use_container_width=True
    )

if analyze_clicked:
    if not job_description.strip():
        st.error("Please enter a job description.")
    elif not uploaded_files:
        st.warning("Please upload at least one resume.")
    else:
        try:
            results, errors = analyze(job_description, uploaded_files)
            st.session_state["results"] = results
            st.session_state["errors"] = errors
        except Exception as error:
            st.error(f"Application error: {error}")

# --------------------------------------------------
# 8. RESULTS
# --------------------------------------------------

results = st.session_state.get("results")
errors = st.session_state.get("errors", [])

if results is not None:
    st.write("")
    st.markdown('<span class="step">Step 3</span>', unsafe_allow_html=True)
    st.subheader("Candidate analysis")

    for err in errors:
        st.error(f"Could not process {err}")

    if not results:
        st.warning("No resumes were successfully analyzed.")
    else:
        avg = sum(c["score"] for c in results) / len(results)
        strong = sum(1 for c in results if c["score"] >= 75)

        s1, s2, s3, s4 = st.columns(4)
        s1.markdown(stat("📄", "Analyzed", len(results)), unsafe_allow_html=True)
        s2.markdown(stat("📊", "Average score", f"{avg:.1f}"), unsafe_allow_html=True)
        s3.markdown(stat("🏆", "Top score", results[0]["score"]), unsafe_allow_html=True)
        s4.markdown(stat("🔥", "Strong matches", strong), unsafe_allow_html=True)

        # ---- DOWNLOADS, right under the stats ----
        st.write("")
        st.markdown("#### 📥 Download results")
        st.download_button(
            "⬇️ Download Results (CSV)",
            data=build_csv(results),
            file_name="candidate_results.csv",
            mime="text/csv",
            use_container_width=True,
        )

        st.write("")
        tab_cards, tab_table = st.tabs(["🏆 Ranked candidates", "📊 Overview table"])

        with tab_cards:
            f1, f2 = st.columns([2, 1])
            min_score = f1.slider("Minimum score", 0, 100, 0)
            search = f2.text_input("Search by name", placeholder="e.g. Priya")

            medals = {1: "🥇", 2: "🥈", 3: "🥉"}
            shown = [
                (rank, c)
                for rank, c in enumerate(results, start=1)
                if c["score"] >= min_score and search.lower() in c["name"].lower()
            ]
            if not shown:
                st.info("No candidates match the current filters.")

            for rank, c in shown:
                color = score_color(c["score"])
                st.markdown(
                    f"""
<div class="cand">
  <div class="medal">{medals.get(rank, f"#{rank}")}</div>
  <div class="ring" style="--p:{c['score']}; --c:{color}"><span>{c['score']}</span></div>
  <div>
    <div class="name">{html.escape(c['name'])}</div>
    <div class="sub">{html.escape(c['email'] or 'No email found')} &nbsp;|&nbsp; {html.escape(c['resume_file'])}</div>
  </div>
  <div class="verdict" style="background:{color}">{html.escape(str(c['verdict']))}</div>
</div>
""",
                    unsafe_allow_html=True,
                )

                with st.expander("View full report"):
                    m1, m2 = st.columns(2)
                    m1.markdown(f"**📧 Email:** {c['email'] or 'Not found'}")
                    m2.markdown(f"**📞 Phone:** {c['phone'] or 'Not found'}")

                    st.markdown("**✅ Matching skills**")
                    st.markdown(chips(c["matching_skills"], "chip-good"), unsafe_allow_html=True)
                    st.markdown("**❌ Missing skills**")
                    st.markdown(chips(c["missing_skills"], "chip-bad"), unsafe_allow_html=True)
                    st.markdown("**⭐ Preferred skills found**")
                    st.markdown(chips(c["preferred_skills_found"], "chip-pref"), unsafe_allow_html=True)

                    s_col, c_col = st.columns(2)
                    with s_col:
                        st.markdown("**💪 Strengths**")
                        for item in c["strengths"]:
                            st.write(f"- {item}")
                    with c_col:
                        st.markdown("**⚠️ Concerns**")
                        for item in c["concerns"]:
                            st.write(f"- {item}")

                    st.markdown("**🧠 AI summary**")
                    st.info(c["summary"])

        with tab_table:
            st.dataframe(
                [
                    {
                        "Rank": rank,
                        "Candidate": c["name"],
                        "Score": c["score"],
                        "Verdict": c["verdict"],
                        "Email": c["email"],
                        "Phone": c["phone"],
                    }
                    for rank, c in enumerate(results, start=1)
                ],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Score": st.column_config.ProgressColumn(
                        "Score", min_value=0, max_value=100, format="%d"
                    )
                },
            )

# --------------------------------------------------
# 9. FOOTER
# --------------------------------------------------

st.markdown(
    f'<div class="footer">Crafted with ❤️ by <b>{AUTHOR}</b> '
    f'&nbsp;|&nbsp; Python, Streamlit, Groq and Pydantic</div>',
    unsafe_allow_html=True,
)
