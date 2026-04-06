# app.py — DataForge: AI Data Science Tutor
# API keys load from .env automatically — no sidebar input needed

import streamlit as st
import pandas as pd
import numpy as np
import os
import time
from dotenv import load_dotenv

# ── Load keys from .env once at startup ───────────────────────────────────
load_dotenv()
OPENAI_KEY  = os.getenv("OPENAI_API_KEY", "")
YOUTUBE_KEY = os.getenv("YOUTUBE_API_KEY", "")
TAVILY_KEY  = os.getenv("TAVILY_API_KEY", "")

# ── Agent imports ──────────────────────────────────────────────────────────
from orchestrator import run_pipeline
from agents.automl           import run_automl
from agents.nl_query         import parse_and_execute, nl_query_gpt
from agents.visualiser_plotly import generate_plotly_charts
from agents.tutor            import get_lesson, get_model_explanation, generate_quiz
from agents.resources        import get_resources, search_resources
from agents.live_resources   import fetch_live_resources, get_topic_from_question
from agents.gpt_tutor        import (generate_lesson, generate_quiz as gpt_generate_quiz,
                                      explain_audit_log, interpret_chart,
                                      generate_feedback, explain_automl_results,
                                      build_dataset_context)
from agents.voice            import text_to_speech, get_audio_html, get_narration, clean_for_speech
from agents.certificate      import generate_certificate, show_certificate_section
from agents.code_export      import generate_notebook, notebook_to_bytes
from agents.bias_report      import run_bias_audit, render_bias_report
from agents.multi_dataset    import compare_datasets
from agents.kaggle_datasets  import recommend_datasets, render_dataset_cards
# student_tracker removed

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DataForge Tutor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color:#0D1117; color:#F0F6FC; }
    section[data-testid="stSidebar"] { background-color:#161B22; }
    section[data-testid="stSidebar"] * { color:#F0F6FC !important; }
    .tutor-title { font-size:2.5rem; font-weight:900; color:#02C39A; margin-bottom:0; }
    .tutor-sub   { font-size:1rem; color:#8B949E; margin-top:0; font-style:italic; }
    .lesson-box  { background:#161B22; border-left:4px solid #02C39A;
                   border-radius:0 8px 8px 0; padding:1.2rem 1.5rem;
                   margin:0.8rem 0; color:#E6EDF3; line-height:1.8; }
    .step-badge  { background:#028090; color:white; border-radius:20px;
                   padding:3px 14px; font-size:0.85rem; font-weight:bold;
                   display:inline-block; margin-bottom:8px; }
    .metric-card { background:#161B22; border:1px solid #028090;
                   border-radius:10px; padding:.9rem 1rem; }
    .metric-val  { font-size:1.8rem; font-weight:800; color:#02C39A; }
    .metric-lbl  { font-size:.8rem; color:#8B949E; }
    .quiz-box    { background:#0D2137; border:1px solid #028090;
                   border-radius:10px; padding:1.2rem; margin:0.8rem 0; }
    .quiz-q      { font-size:1rem; font-weight:700; color:#E6EDF3; margin-bottom:0.8rem; }
    .correct     { background:#166534; border-radius:8px; padding:0.6rem 1rem;
                   color:#86EFAC; font-weight:bold; }
    .wrong       { background:#7F1D1D; border-radius:8px; padding:0.6rem 1rem;
                   color:#FCA5A5; font-weight:bold; }
    .explanation { background:#1C2333; border-radius:8px; padding:0.8rem;
                   color:#94A3B8; font-size:0.9rem; margin-top:0.5rem; }
    .chat-user   { background:#1C2333; border-radius:12px 12px 2px 12px;
                   padding:0.8rem 1rem; margin:0.4rem 0; color:#E6EDF3;
                   max-width:80%; float:right; clear:both; }
    .chat-tutor  { background:#161B22; border:1px solid #028090;
                   border-radius:2px 12px 12px 12px;
                   padding:0.8rem 1rem; margin:0.4rem 0; color:#E6EDF3;
                   max-width:85%; float:left; clear:both; }
    .chat-wrap   { overflow:hidden; margin-bottom:0.5rem; }
    .audit-entry { background:#161B22; border-left:3px solid #028090;
                   padding:5px 12px; margin:3px 0; border-radius:0 6px 6px 0;
                   font-size:.85rem; font-family:monospace; color:#C9D1D9; }
    .automl-best { background:linear-gradient(135deg,#028090,#02C39A);
                   border-radius:10px; padding:1rem; color:white; text-align:center; }
    .automl-score { font-size:2rem; font-weight:900; }
    #MainMenu{visibility:hidden} footer{visibility:hidden}
    .stButton>button { background-color:#02C39A; color:#0D1117;
                       font-weight:700; border:none; border-radius:6px; }
    .stButton>button:hover { background-color:#028090; color:white; }
    .stTabs [data-baseweb="tab"] { color:#8B949E; }
    .stTabs [aria-selected="true"] { color:#02C39A !important;
                                      border-bottom-color:#02C39A !important; }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────
for key, default in [
    ("level", "beginner"), ("chat_history", []),
    ("quiz_answers", {}),  ("steps_completed", []), ("score", 0),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Set up OpenAI client from .env ────────────────────────────────────────
use_gpt    = False
gpt_client = None
if OPENAI_KEY:
    try:
        from openai import OpenAI
        gpt_client = OpenAI(api_key=OPENAI_KEY)
        use_gpt    = True
    except Exception:
        pass

use_live = bool(YOUTUBE_KEY or TAVILY_KEY)


# ── Helpers ────────────────────────────────────────────────────────────────
def lesson_box(text: str):
    """Renders text inside a styled lesson box."""
    st.markdown(f'<div class="lesson-box">{text}</div>', unsafe_allow_html=True)


def speak(text: str, label: str = "Listen", key_suffix: str = ""):
    """
    Renders a voice narration button.
    Generates audio from OpenAI TTS and embeds an HTML player.
    Always reads gpt_client from session_state so it works
    both before and after the pipeline runs.
    Only shows if OpenAI key is available.
    """
    # Always get the latest client — works before and after pipeline
    _client = st.session_state.get("gpt_client", gpt_client)
    _use    = st.session_state.get("use_gpt", use_gpt)

    if not _use or not _client:
        return

    if not text or not text.strip():
        return

    btn_key   = f"speak_btn_{abs(hash(text[:80]))}{key_suffix}"
    voice_key = f"speak_voice_{abs(hash(text[:80]))}{key_suffix}"
    cache_key = f"audio_{abs(hash(text[:80]))}{key_suffix}"

    col1, col2 = st.columns([2, 3])
    with col1:
        clicked = st.button(f"🔊 {label}", key=btn_key)
    with col2:
        voice_choice = st.selectbox(
            "Voice",
            options=["nova", "alloy", "echo", "fable", "onyx", "shimmer"],
            index=0,
            key=voice_key,
            label_visibility="collapsed"
        )

    if clicked:
        if cache_key not in st.session_state:
            with st.spinner("Generating audio..."):
                audio_bytes = text_to_speech(text, _client, voice=voice_choice)
                st.session_state[cache_key] = audio_bytes

        audio = st.session_state.get(cache_key)
        if audio:
            st.markdown(get_audio_html(audio), unsafe_allow_html=True)
        else:
            st.warning("Audio generation failed — check your OpenAI API key.")


def show_resources(topic: str, level: str = "beginner", expanded: bool = False):
    """Shows live or curated resources in a collapsible panel."""
    if use_live:
        with st.spinner("Searching for resources..."):
            res = fetch_live_resources(
                topic, level,
                youtube_key=YOUTUBE_KEY or None,
                tavily_key=TAVILY_KEY or None
            )
        label = "🌐 Live results"
    else:
        res   = get_resources(topic, level)
        label = "📚 Curated resources"

    videos   = res.get("videos", [])
    articles = res.get("articles", [])
    total    = len(videos) + len(articles)
    if total == 0:
        return

    with st.expander(f"📚 Further Learning — {total} resources ({label})", expanded=expanded):
        if videos:
            st.markdown("#### 🎬 Watch")
            for v in videos:
                c1, c2 = st.columns([4, 1])
                with c1:
                    why = v.get("why", v.get("description", ""))
                    st.markdown(f"**[{v['title']}]({v['url']})**  \n"
                                f"📺 *{v['channel']}* · ⏱ {v.get('duration','')}  \n"
                                f"*{why[:120]}*")
                with c2:
                    st.link_button("▶ Watch", v["url"])
        if articles:
            st.markdown("#### 📰 Read")
            for a in articles:
                c1, c2 = st.columns([4, 1])
                with c1:
                    why = a.get("why", a.get("snippet", ""))
                    st.markdown(f"**[{a['title']}]({a['url']})**  \n"
                                f"📖 *{a['source']}*  \n"
                                f"*{why[:120]}*")
                with c2:
                    st.link_button("📖 Read", a["url"])


def render_quiz(questions: list, prefix: str):
    """Renders quiz questions with scoring and explanations."""
    for qi, q in enumerate(questions):
        key = f"{prefix}_q{qi}"
        st.markdown(
            f'<div class="quiz-box"><div class="quiz-q">Q{qi+1}: {q["q"]}</div></div>',
            unsafe_allow_html=True
        )
        choice = st.radio("Your answer:", q["options"],
                          key=key, index=None, label_visibility="collapsed")
        if choice:
            ans_idx = q["options"].index(choice)
            if key not in st.session_state["quiz_answers"]:
                st.session_state["quiz_answers"][key] = ans_idx
                if ans_idx == q["answer"]:
                    st.session_state["score"] += 10
            if st.session_state["quiz_answers"].get(key) == q["answer"]:
                st.markdown('<div class="correct">✅ Correct! +10 points</div>',
                            unsafe_allow_html=True)
            else:
                st.markdown('<div class="wrong">❌ Not quite — try again</div>',
                            unsafe_allow_html=True)
            st.markdown(f'<div class="explanation">💡 {q["explanation"]}</div>',
                        unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# SIDEBAR — no API key inputs, keys come from .env
# ══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🎓 DataForge Tutor")
    st.markdown("*Your AI Data Science Mentor*")
    st.divider()

    # AI status indicators
    st.markdown("### ⚙️ AI Status")
    if use_gpt:
        st.success("GPT-4 enabled ✅")
    else:
        st.info("Built-in tutor mode")
    if use_live:
        st.success("Live resources ✅")
    else:
        st.caption("Using curated resource list")
    st.divider()

    # Level selector
    st.markdown("### 📚 Your Level")
    level_pick = st.radio(
        "Choose your level:",
        ["Beginner", "Intermediate"],
        index=0 if st.session_state["level"] == "beginner" else 1
    )
    st.session_state["level"] = level_pick.lower()
    st.divider()

    # Progress
    st.markdown("### 📊 Your Progress")
    done_steps = [s.lower() for s in st.session_state["steps_completed"]]
    for step in ["Upload", "Clean", "Analyse", "Visualise", "AutoML", "Chat"]:
        icon = "✅" if step.lower() in done_steps else "⭕"
        st.markdown(f"{icon} {step}")
    st.divider()

    # Score
    st.markdown(f"### 🏆 Quiz Score: {st.session_state['score']} pts")
    st.progress(len(set(done_steps)) / 6)
    st.caption(f"{len(set(done_steps))}/6 steps complete")
    st.divider()

    # Student name for certificate
    st.markdown("### 👤 Your Name")
    st.text_input("Name (for certificate)", placeholder="Enter your name...",
                  key="student_name")
    st.divider()

    # Voice settings
    st.markdown("### 🔊 Voice Narration")
    if use_gpt:
        st.markdown("Click **🔊 Listen** buttons throughout the app to hear lessons read aloud.")
        st.caption("Powered by OpenAI TTS · 6 voices available")
    else:
        st.caption("Add OPENAI_API_KEY to .env to enable voice narration")


# ══════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<p class="tutor-title">🎓 DataForge — AI Data Science Tutor</p>',
            unsafe_allow_html=True)
st.markdown('<p class="tutor-sub">Learn the complete data science pipeline — '
            'step by step, with explanations, quizzes and personalised teaching</p>',
            unsafe_allow_html=True)
st.divider()

level = st.session_state["level"]

# ══════════════════════════════════════════════════════════════════════════
# WELCOME SCREEN
# ══════════════════════════════════════════════════════════════════════════
if "intro_shown" not in st.session_state:
    with st.expander("👋 Welcome — Read This First!", expanded=True):
        intro_text = get_lesson("intro", level=level)
        st.markdown(intro_text)
        speak(get_narration("welcome"), label="Listen to Welcome", key_suffix="welcome")
        show_resources("data_science_intro", level, expanded=False)
        if st.button("✅ Got it — Let's Start!"):
            st.session_state["intro_shown"] = True
            st.rerun()
    st.stop()

# ══════════════════════════════════════════════════════════════════════════
# STEP 1 — UPLOAD
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<span class="step-badge">📂 Step 1: Upload Your Dataset</span>',
            unsafe_allow_html=True)
st.markdown("""
> 💡 **What is a dataset?** A dataset is data organised in rows and columns — like a spreadsheet.
> Each **row** is one observation. Each **column** is one feature.
""")

uploaded = st.file_uploader("Upload a CSV or Excel file:", type=["csv", "xlsx", "xls"])
use_demo = st.checkbox("🎯 Use the built-in demo dataset (recommended for beginners)")

# ── Multi-dataset comparison option ───────────────────────────────────────
with st.expander("📂 Compare Two Datasets (optional)", expanded=False):
    st.markdown("Upload a second dataset to compare side by side with your main one.")
    uploaded2 = st.file_uploader("Second dataset (optional):",
                                  type=["csv","xlsx","xls"], key="second_file")
    if uploaded2:
        try:
            df2 = (pd.read_csv(uploaded2) if uploaded2.name.endswith(".csv")
                   else pd.read_excel(uploaded2))
            st.session_state["df2"]        = df2
            st.session_state["df2_name"]   = uploaded2.name
            st.success(f"✅ Second dataset loaded: {df2.shape[0]:,} rows × {df2.shape[1]} columns")
        except Exception as e:
            st.error(f"Failed to read second file: {e}")

# ── Kaggle dataset suggestions ─────────────────────────────────────────────
with st.expander("💡 Not sure what dataset to use? Browse recommendations", expanded=False):
    st.markdown("**Find a free dataset on Kaggle to practise with:**")
    goal_options = ["classification", "regression", "clustering", "time_series", "education"]
    goal = st.selectbox("What do you want to learn?", goal_options, key="kaggle_goal")
    kaggle_datasets = recommend_datasets(goal, level)
    render_dataset_cards(st, kaggle_datasets)

df_raw = None
if use_demo:
    rng = np.random.default_rng(42)
    n   = 400
    df_raw = pd.DataFrame({
        "age":            rng.integers(18, 70, n).astype(float),
        "income":         rng.exponential(40000, n),
        "spending_score": rng.normal(50, 20, n),
        "visits":         rng.poisson(5, n).astype(float),
        "region":         rng.choice(["North","South","East","West",None], n),
        "customer_type":  rng.choice(["Premium","Standard","Basic"], n),
        "satisfaction":   rng.choice([1,2,3,4,5,None], n),
        "churn":          rng.choice([0,1], n),
    })
    idx = rng.choice(n, 40, replace=False)
    df_raw.loc[idx, "age"]         = None
    df_raw.loc[idx[:10], "income"] = None
    df_raw = pd.concat([df_raw, df_raw.iloc[:15]], ignore_index=True)
    st.success(f"✅ Demo dataset loaded: {df_raw.shape[0]} rows × {df_raw.shape[1]} columns")
    st.markdown("> 📖 Fictional customer dataset with intentional missing values and duplicates "
                "so you can see DataForge clean them!")

elif uploaded:
    try:
        df_raw = (pd.read_csv(uploaded) if uploaded.name.endswith(".csv")
                  else pd.read_excel(uploaded))
        st.success(f"✅ **{uploaded.name}** — {df_raw.shape[0]:,} rows × {df_raw.shape[1]} columns")
    except Exception as e:
        st.error(f"Failed to read file: {e}")

if df_raw is not None:
    with st.expander("👀 Preview raw data (first 10 rows)", expanded=True):
        st.dataframe(df_raw.head(10), use_container_width=True)
        st.markdown(f"> 📖 Your dataset has **{df_raw.shape[0]:,} rows** and "
                    f"**{df_raw.shape[1]} columns**. Empty cells = missing values DataForge will fix.")

    if "upload" not in done_steps:
        st.session_state["steps_completed"].append("upload")

    st.divider()

    # ── STEP 2 — DATA CLEANING LESSON ─────────────────────────────────────
    st.markdown('<span class="step-badge">🧹 Step 2: Data Cleaning</span>',
                unsafe_allow_html=True)
    with st.expander("📖 Learn: What is Data Cleaning?", expanded=True):
        st.markdown(get_lesson("cleaning", "intro", level))

    if st.button("🚀 Run DataForge Pipeline", key="run_pipeline"):
        prog   = st.progress(0)
        status = st.empty()
        def on_prog(step, msg):
            prog.progress(int((step / 5) * 100))
            status.markdown(f"**{msg}**")
        start   = time.time()
        results = run_pipeline(df_raw, use_gpt=use_gpt, progress_callback=on_prog)
        elapsed = round(time.time() - start, 2)
        prog.progress(100)
        if not results["success"]:
            st.error(f"❌ {results['error']}")
            st.stop()
        status.markdown(f"✅ **Pipeline complete in {elapsed}s!**")
        st.session_state.update({
            "results": results, "elapsed": elapsed, "df_raw": df_raw,
            "gpt_client": gpt_client, "use_gpt": use_gpt,
        })
        for s in ["clean", "analyse", "visualise"]:
            if s not in done_steps:
                st.session_state["steps_completed"].append(s)
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════
# RESULTS — shown after pipeline runs
# ══════════════════════════════════════════════════════════════════════════
if "results" not in st.session_state:
    st.stop()

results    = st.session_state["results"]
elapsed    = st.session_state["elapsed"]
df_raw     = st.session_state.get("df_raw", df_raw)
cleaned    = results["cleaned_df"]
audit      = results["audit_log"]
insights   = results["insights"]
report     = results["report"]
level      = st.session_state["level"]
gpt_client = st.session_state.get("gpt_client", gpt_client)
use_gpt    = st.session_state.get("use_gpt", use_gpt)
ds_ctx     = build_dataset_context(cleaned, insights, audit)

# KPI row
st.divider()
k1, k2, k3, k4 = st.columns(4)
for col_st, val, lbl in [
    (k1, f"{cleaned.shape[0]:,}", "Clean Rows"),
    (k2, cleaned.shape[1],        "Columns"),
    (k3, f"{elapsed}s",           "Runtime"),
    (k4, len(insights.get("strong_correlations", [])), "Correlations"),
]:
    col_st.markdown(
        f'<div class="metric-card"><div class="metric-val">{val}</div>'
        f'<div class="metric-lbl">{lbl}</div></div>',
        unsafe_allow_html=True
    )
st.markdown("")

# ══════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════
t1, t2, t3, t4, t5, t6, t7, t8 = st.tabs([
    "🧹 Cleaning", "📊 Analysis", "📈 Visualisation",
    "🤖 AutoML", "💬 Ask the Tutor", "📝 Report",
    "⚖️ Bias Report", "🤝 Collaborate",
])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — CLEANING
# ════════════════════════════════════════════════════════════════════════════
with t1:
    n_dupes   = sum(1 for e in audit if "duplicate" in e.lower())
    n_missing = sum(1 for e in audit if "missing" in e.lower())

    st.markdown("### 📖 Understanding Your Data Cleaning Results")

    if use_gpt and gpt_client:
        if "lesson_cleaning" not in st.session_state:
            with st.spinner("GPT-4 is personalising your lesson..."):
                st.session_state["lesson_cleaning"] = generate_lesson(
                    gpt_client, "cleaning", level, ds_ctx)
        lesson_box(st.session_state["lesson_cleaning"])
        speak(st.session_state["lesson_cleaning"], label="Listen to Lesson", key_suffix="clean_lesson")
    else:
        static_lesson = (get_lesson("cleaning", "missing_values", level, {"missing_count": n_missing})
                         + "\n\n" + get_lesson("cleaning", "duplicates", level, {"n_duplicates": n_dupes})
                         + "\n\n" + get_lesson("cleaning", "outliers", level))
        lesson_box(static_lesson)
        speak(get_narration("cleaning_intro"), label="Listen to Lesson", key_suffix="clean_static")

    st.markdown("### 📋 What DataForge Did to Your Data")
    for entry in audit:
        st.markdown(f'<div class="audit-entry">{entry}</div>', unsafe_allow_html=True)

    if use_gpt and gpt_client:
        st.markdown("### 💡 GPT-4 Explanation")
        if "lesson_audit" not in st.session_state:
            with st.spinner("Explaining your cleaning results..."):
                st.session_state["lesson_audit"] = explain_audit_log(gpt_client, audit, level)
        lesson_box(st.session_state["lesson_audit"])
        speak(st.session_state["lesson_audit"], label="Listen to Explanation", key_suffix="audit_exp")

    st.markdown("### ✅ Your Cleaned Dataset")
    st.dataframe(cleaned, use_container_width=True)
    st.download_button("⬇️ Download Cleaned CSV",
                       cleaned.to_csv(index=False).encode(),
                       "cleaned_data.csv", "text/csv")

    show_resources("cleaning", level)
    st.divider()
    st.markdown("### 🧠 Quick Quiz — Test Your Understanding!")
    speak(get_narration("quiz_intro"), label="Listen to Quiz Intro", key_suffix="clean_quiz_intro")

    if use_gpt and gpt_client:
        if "cleaning_quiz_q" not in st.session_state:
            with st.spinner("GPT-4 is generating quiz questions from your data..."):
                st.session_state["cleaning_quiz_q"] = gpt_generate_quiz(
                    gpt_client, "cleaning", level, ds_ctx)
        questions = st.session_state["cleaning_quiz_q"]
    else:
        questions = generate_quiz("cleaning", level)
    render_quiz(questions, "clean")

    if use_gpt and gpt_client and st.session_state["quiz_answers"]:
        clean_keys = [k for k in st.session_state["quiz_answers"] if k.startswith("clean_q")]
        if clean_keys and "clean_feedback" not in st.session_state:
            wrong_qs = [q["q"] for qi, q in enumerate(questions)
                        if st.session_state["quiz_answers"].get(f"clean_q{qi}") != q["answer"]]
            with st.spinner("GPT-4 is preparing your personalised feedback..."):
                st.session_state["clean_feedback"] = generate_feedback(
                    gpt_client, "cleaning", level,
                    len(clean_keys) - len(wrong_qs), len(clean_keys), wrong_qs)
        if "clean_feedback" in st.session_state:
            st.markdown("### 🎯 Your Personalised Feedback")
            lesson_box(st.session_state["clean_feedback"])
            speak(st.session_state["clean_feedback"], label="Listen to Feedback", key_suffix="clean_fb")


# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — ANALYSIS
# ════════════════════════════════════════════════════════════════════════════
with t2:
    if use_gpt and gpt_client:
        if "lesson_analysis" not in st.session_state:
            with st.spinner("GPT-4 is personalising your statistics lesson..."):
                st.session_state["lesson_analysis"] = generate_lesson(
                    gpt_client, "analysis", level, ds_ctx)
        lesson_box(st.session_state["lesson_analysis"])
        speak(st.session_state["lesson_analysis"], label="Listen to Lesson", key_suffix="analysis_lesson")
    else:
        static_a = get_lesson("analysis", "intro", level)
        lesson_box(static_a)
        speak(get_narration("analysis_intro"), label="Listen to Lesson", key_suffix="analysis_static")

    if insights.get("numeric_summary"):
        st.markdown("### 📊 Your Dataset Statistics")
        st.dataframe(pd.DataFrame(insights["numeric_summary"]).T.round(3),
                     use_container_width=True)
        if level == "beginner":
            st.markdown("> 💡 count = total values · mean = average · std = spread · "
                        "25%/50%/75% = quartiles · min/max = range")

    if insights.get("strong_correlations"):
        st.markdown("### 🔗 Correlations Found")
        for p in insights["strong_correlations"]:
            d        = "🟢 Positive" if p["correlation"] > 0 else "🔴 Negative"
            strength = "strong" if abs(p["correlation"]) > 0.7 else "moderate"
            st.markdown(f"- **{p['col_a']}** ↔ **{p['col_b']}**: {d} {strength} (r = `{p['correlation']}`)")
            if level == "beginner":
                st.markdown(f"  *As {p['col_a']} goes {'up' if p['correlation']>0 else 'down'}, "
                            f"{p['col_b']} tends to go {'up' if p['correlation']>0 else 'down'} too.*")

    skewed = insights.get("skewed_columns", {})
    if skewed:
        lesson_box(get_lesson("analysis", "skewness", level))
        st.markdown("**Skewed columns in your dataset:**")
        for col, val in skewed.items():
            direction = "positively (right tail)" if val > 0 else "negatively (left tail)"
            st.markdown(f"- **{col}**: skewness = {val:.2f} — {direction}")

    if insights.get("bias_warnings"):
        st.markdown("### ⚠️ Bias Warnings")
        for w in insights["bias_warnings"]:
            st.warning(w)

    show_resources("analysis", level)
    st.divider()
    st.markdown("### 🧠 Quiz — Statistics & Analysis")
    speak(get_narration("quiz_intro"), label="Listen to Quiz Intro", key_suffix="analysis_quiz_intro")

    if use_gpt and gpt_client:
        if "analysis_quiz_q" not in st.session_state:
            with st.spinner("GPT-4 is generating questions from your findings..."):
                st.session_state["analysis_quiz_q"] = gpt_generate_quiz(
                    gpt_client, "analysis", level, ds_ctx)
        questions = st.session_state["analysis_quiz_q"]
    else:
        questions = generate_quiz("analysis", level)
    render_quiz(questions, "analysis")


# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — VISUALISATION
# ════════════════════════════════════════════════════════════════════════════
with t3:
    if use_gpt and gpt_client:
        if "lesson_viz" not in st.session_state:
            with st.spinner("GPT-4 is personalising your visualisation lesson..."):
                st.session_state["lesson_viz"] = generate_lesson(
                    gpt_client, "visualisation", level, ds_ctx)
        lesson_box(st.session_state["lesson_viz"])
        speak(st.session_state["lesson_viz"], label="Listen to Lesson", key_suffix="viz_lesson")
    else:
        static_v = get_lesson("visualisation", "intro", level)
        lesson_box(static_v)
        speak(get_narration("visualisation_intro"), label="Listen to Lesson", key_suffix="viz_static")

    with st.spinner("Generating interactive charts..."):
        plotly_charts = generate_plotly_charts(cleaned, insights)

    chart_lessons = {
        "Numeric Distributions": "histogram",
        "Correlation Heatmap":   "heatmap",
        "Outlier Detection":     "boxplot",
        "Scatter":               "scatter",
    }

    if plotly_charts:
        for chart in plotly_charts:
            lesson_key = next(
                (v for k, v in chart_lessons.items()
                 if k.lower() in chart["title"].lower()), None
            )
            if lesson_key:
                with st.expander(f"📖 How to read: {chart['title']}", expanded=False):
                    st.markdown(get_lesson("visualisation", lesson_key, level))

            st.markdown(f"**{chart['title']}**")
            st.plotly_chart(chart["fig"], use_container_width=True,
                            config={"displayModeBar": True})

            if use_gpt and gpt_client:
                ck = f"chart_interp_{chart['title'].replace(' ','_')}"
                if ck not in st.session_state:
                    with st.spinner("GPT-4 is interpreting this chart..."):
                        st.session_state[ck] = interpret_chart(
                            gpt_client, chart["title"],
                            chart["title"].split()[0].lower(),
                            level, insights)
                with st.expander("💡 What does this chart tell us?", expanded=True):
                    st.markdown(st.session_state[ck])
            st.markdown("")

    show_resources("visualisation", level)
    st.divider()
    st.markdown("### 🧠 Quiz — Data Visualisation")
    speak(get_narration("quiz_intro"), label="Listen to Quiz Intro", key_suffix="viz_quiz_intro")

    if use_gpt and gpt_client:
        if "viz_quiz_q" not in st.session_state:
            with st.spinner("GPT-4 is generating visualisation questions..."):
                st.session_state["viz_quiz_q"] = gpt_generate_quiz(
                    gpt_client, "visualisation", level, ds_ctx)
        questions = st.session_state["viz_quiz_q"]
    else:
        questions = generate_quiz("visualisation", level)
    render_quiz(questions, "viz")


# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — AUTOML
# ════════════════════════════════════════════════════════════════════════════
with t4:
    if use_gpt and gpt_client:
        if "lesson_automl" not in st.session_state:
            with st.spinner("GPT-4 is personalising your machine learning lesson..."):
                st.session_state["lesson_automl"] = generate_lesson(
                    gpt_client, "automl", level, ds_ctx)
        lesson_box(st.session_state["lesson_automl"])
        speak(st.session_state["lesson_automl"], label="Listen to Lesson", key_suffix="automl_lesson")
    else:
        static_ml = get_lesson("automl", "intro", level)
        lesson_box(static_ml)
        speak(get_narration("automl_intro"), label="Listen to Lesson", key_suffix="automl_static")

    st.markdown("### 🎯 Train a Model on Your Data")
    target = st.selectbox("Select the column you want to predict:",
                          options=cleaned.columns.tolist())
    if level == "beginner":
        st.markdown(f"> 💡 You're telling the model: 'Given all other columns, "
                    f"can you predict **{target}**?' DataForge will test multiple "
                    f"algorithms and find the best one.")

    if st.button("🚀 Run AutoML", key="automl_btn"):
        with st.spinner("Training and comparing models..."):
            ml_res = run_automl(cleaned, target)

        if ml_res.get("error"):
            st.error(f"AutoML Error: {ml_res['error']}")
        else:
            task   = ml_res["task_type"]
            best   = ml_res["best_model"]
            score  = ml_res["best_score"]
            metric = ml_res["best_metric"]

            st.markdown(
                f'<div class="automl-best">'
                f'<div style="font-size:.9rem;opacity:.85">🏆 Best Model for predicting {target}</div>'
                f'<div class="automl-score">{best}</div>'
                f'<div style="font-size:1.1rem">{metric}: {score:.1%}</div>'
                f'<div style="font-size:.85rem;opacity:.75;margin-top:.3rem">Task: {task.title()}</div>'
                f'</div>', unsafe_allow_html=True
            )
            st.markdown("")

            if use_gpt and gpt_client:
                if "lesson_ml_exp" not in st.session_state:
                    with st.spinner("GPT-4 is explaining your results..."):
                        st.session_state["lesson_ml_exp"] = explain_automl_results(
                            gpt_client, ml_res, level)
                lesson_box(st.session_state["lesson_ml_exp"])
                speak(st.session_state["lesson_ml_exp"], label="Listen to ML Explanation", key_suffix="ml_exp")
            else:
                static_ml_exp = get_model_explanation(best, level)
                lesson_box(static_ml_exp)
                speak(static_ml_exp, label="Listen to Model Explanation", key_suffix="ml_static_exp")

            st.markdown("### 🏁 All Models Compared")
            mdf = pd.DataFrame(ml_res["models"])
            st.dataframe(mdf.style.background_gradient(subset=["score"], cmap="YlGn"),
                         use_container_width=True)

            with st.expander("📖 What are all these algorithms?"):
                for row in ml_res["models"]:
                    st.markdown(f"**{row['name']}** (score: {row['score']:.1%})")
                    st.markdown(get_model_explanation(row["name"], level))
                    st.markdown("---")

            if ml_res.get("feature_importance"):
                st.markdown("### 🔍 Feature Importance")
                if level == "beginner":
                    st.markdown("> 💡 Taller bars = more important for predictions")
                import plotly.express as px
                fi_df = pd.DataFrame(list(ml_res["feature_importance"].items()),
                                     columns=["Feature", "Importance"])
                fig = px.bar(fi_df, x="Importance", y="Feature", orientation="h",
                             color="Importance",
                             color_continuous_scale=["#028090","#02C39A"])
                fig.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                                  showlegend=False, coloraxis_showscale=False,
                                  yaxis=dict(autorange="reversed"))
                st.plotly_chart(fig, use_container_width=True)

            lesson_box(get_lesson("automl", "metrics", level))
            show_resources("automl", level)
            st.divider()
            st.markdown("### 🧠 Quiz — Machine Learning")
            speak(get_narration("quiz_intro"), label="Listen to Quiz Intro", key_suffix="ml_quiz_intro")

            if use_gpt and gpt_client:
                ml_ctx_quiz = dict(ds_ctx)
                ml_ctx_quiz.update({
                    "target_col": target, "task_type": task,
                    "best_model": best,   "best_score": score,
                    "metric_name": metric,
                    "worst_model": ml_res["models"][-1]["name"] if ml_res.get("models") else "unknown"
                })
                if "automl_quiz_q" not in st.session_state:
                    with st.spinner("GPT-4 is generating ML quiz questions..."):
                        st.session_state["automl_quiz_q"] = gpt_generate_quiz(
                            gpt_client, "automl", level, ml_ctx_quiz)
                questions = st.session_state["automl_quiz_q"]
            else:
                questions = generate_quiz("automl", level)
            render_quiz(questions, "ml")

            if "automl" not in st.session_state["steps_completed"]:
                st.session_state["steps_completed"].append("automl")


# ════════════════════════════════════════════════════════════════════════════
# TAB 5 — ASK THE TUTOR
# ════════════════════════════════════════════════════════════════════════════
with t5:
    st.markdown("### 💬 Ask the DataForge Tutor")
    st.markdown("Ask anything about your data or data science concepts!")

    num_cols = cleaned.select_dtypes(include=[np.number]).columns.tolist()
    suggestions = [
        "What does standard deviation mean?",
        "Why is my data skewed?",
        "How many missing values were there?",
        f"What is the average {num_cols[0]}?" if num_cols else "What are the statistics?",
        "What is overfitting?",
        "How do I improve model accuracy?",
        "What are the correlations?",
        "Are there any outliers?",
    ]

    st.markdown("**💡 Suggested questions:**")
    scols = st.columns(4)
    for i, sug in enumerate(suggestions):
        with scols[i % 4]:
            if st.button(sug, key=f"sug_{i}"):
                st.session_state["nl_q"] = sug

    st.markdown("---")
    question = st.text_input(
        "Ask a question:",
        value=st.session_state.get("nl_q", ""),
        placeholder="e.g. What does correlation mean?",
        key="chat_input"
    )

    if st.button("💬 Ask", key="ask_btn") and question:
        data_keywords = ["how many","what is the","average","mean","max","min",
                         "correlation","missing","outlier","unique","distribution",
                         "show me","top","count"]
        is_data_q = any(kw in question.lower() for kw in data_keywords)

        if is_data_q:
            if use_gpt and gpt_client:
                qr = nl_query_gpt(cleaned, question, gpt_client)
            else:
                qr = parse_and_execute(cleaned, question)
            answer = qr.get("answer", "I couldn't process that question.")
            code   = qr.get("code", "")
        else:
            concept_answers = {
                "standard deviation": "**Standard deviation** measures how spread out your data is. Small std = values cluster near the average. Large std = values are very spread out.",
                "overfitting": "**Overfitting** is when a model memorises training data instead of learning patterns. It scores well on training data but fails on new data. Fix: cross-validation, simpler models, or more data.",
                "underfitting": "**Underfitting** means the model is too simple — it can't capture the patterns. Fix: more complex models or more features.",
                "correlation": "**Correlation** measures how strongly two variables are related. r = +1 (both go up together), r = -1 (one goes up, the other down), r = 0 (no relationship). Remember: correlation ≠ causation!",
                "accuracy": "**Accuracy** = correct predictions / total predictions. 90% means 9/10 correct. Warning: a model that always predicts the majority class gets high accuracy without learning anything!",
                "feature importance": "**Feature importance** shows which columns had the most influence on the model's predictions. High importance = that column was very helpful for predictions.",
                "skewness": "**Skewness** measures how lopsided a distribution is. Positive skew = long right tail (a few very high values). Negative skew = long left tail. Fix: log transformation.",
                "cross-validation": "**Cross-validation** tests your model multiple times on different data splits to get a more reliable performance estimate.",
            }
            answer = next(
                (v for k, v in concept_answers.items() if k in question.lower()),
                "Great question! Try asking about your actual data — like 'what is the average income?' or 'are there outliers?'"
            )
            if use_gpt and gpt_client:
                resp = gpt_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": f"You are a friendly data science tutor teaching a {level} student. Be clear, use analogies, keep under 150 words."},
                        {"role": "user", "content": question}
                    ],
                    max_tokens=300, temperature=0.5
                )
                answer = resp.choices[0].message.content
            code = ""

        st.session_state["chat_history"].append({"role": "user",  "text": question})
        st.session_state["chat_history"].append({"role": "tutor", "text": answer, "code": code})
        st.session_state["nl_q"] = ""
        # Audio cached for chat — rendered by speak() button above

    if st.session_state["chat_history"]:
        st.markdown("### 💬 Conversation")
        for msg in reversed(st.session_state["chat_history"]):
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-wrap"><div class="chat-user">🧑‍🎓 {msg["text"]}</div></div>',
                            unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-wrap"><div class="chat-tutor">🎓 {msg["text"]}</div></div>',
                            unsafe_allow_html=True)
                if msg.get("code"):
                    with st.expander("📋 Code"):
                        st.code(msg["code"], language="python")
                speak(msg["text"], label="Listen to Answer",
                      key_suffix=f"chat_{abs(hash(msg['text'][:60]))}_idx")

        # Resource suggestions after question
        last_q = next((m["text"] for m in reversed(st.session_state["chat_history"])
                       if m["role"] == "user"), "")
        if last_q:
            topic = get_topic_from_question(last_q)
            if use_live:
                with st.spinner("Finding resources..."):
                    suggested = fetch_live_resources(topic, level,
                                                      youtube_key=YOUTUBE_KEY or None,
                                                      tavily_key=TAVILY_KEY or None)
            else:
                suggested = search_resources(last_q, level)

            vids = suggested.get("videos", [])[:2]
            arts = suggested.get("articles", [])[:2]
            if vids or arts:
                with st.expander("📚 Resources related to your question", expanded=True):
                    for v in vids:
                        c1, c2 = st.columns([4, 1])
                        with c1:
                            st.markdown(f"**[{v['title']}]({v['url']})**  \n"
                                        f"📺 *{v['channel']}* · ⏱ {v.get('duration','')}  \n"
                                        f"*{v.get('why', '')[:100]}*")
                        with c2:
                            st.link_button("▶ Watch", v["url"])
                    for a in arts:
                        c1, c2 = st.columns([4, 1])
                        with c1:
                            st.markdown(f"**[{a['title']}]({a['url']})**  \n"
                                        f"📖 *{a['source']}*  \n"
                                        f"*{a.get('why', '')[:100]}*")
                        with c2:
                            st.link_button("📖 Read", a["url"])

        if st.button("🗑️ Clear chat"):
            st.session_state["chat_history"] = []
            st.rerun()

    if "chat" not in st.session_state["steps_completed"]:
        st.session_state["steps_completed"].append("chat")


# ════════════════════════════════════════════════════════════════════════════
# TAB 6 — REPORT
# ════════════════════════════════════════════════════════════════════════════
with t6:
    st.markdown("### 📝 Auto-Generated Analysis Report")
    st.markdown("> 💡 This report was written automatically by DataForge's reporter agent.")
    speak(report[:1000], label="Listen to Report Summary", key_suffix="report_narration")
    st.markdown(report)

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.download_button("⬇️ Download Report (.md)",
                           report.encode(), "dataforge_report.md", "text/markdown")
    with col_r2:
        # Code Export — download as Jupyter notebook
        if st.button("📓 Export as Jupyter Notebook"):
            with st.spinner("Generating notebook..."):
                dataset_name = st.session_state.get("df2_name",
                               getattr(df_raw, "name", "dataset.csv")
                               if df_raw is not None else "dataset.csv")
                notebook = generate_notebook(
                    df_raw if df_raw is not None else cleaned,
                    cleaned, insights, audit,
                    dataset_name=dataset_name
                )
                nb_bytes = notebook_to_bytes(notebook)
            st.download_button(
                "⬇️ Download Notebook (.ipynb)",
                nb_bytes,
                "dataforge_analysis.ipynb",
                "application/json",
                key="dl_notebook"
            )
            st.success("✅ Notebook ready! Open in Jupyter or VS Code to run it.")

    # Multi-dataset comparison section
    if st.session_state.get("df2") is not None and df_raw is not None:
        st.divider()
        st.markdown("### 📊 Multi-Dataset Comparison")
        st.markdown("*Comparing your two uploaded datasets:*")
        with st.spinner("Comparing datasets..."):
            comparison = compare_datasets(
                df_raw, st.session_state["df2"],
                name1="Dataset 1",
                name2=st.session_state.get("df2_name", "Dataset 2")
            )
        # Summary
        st.markdown("**Key Findings:**")
        for s in comparison.get("summary", []):
            st.markdown(f"- {s}")
        # Stats comparison table
        if comparison.get("stats_comparison"):
            st.markdown("**Statistics Comparison:**")
            rows = []
            for col, stats in comparison["stats_comparison"].items():
                for ds, vals in stats.items():
                    rows.append({"Column": col, "Dataset": ds,
                                 "Mean": vals["mean"], "Std": vals["std"],
                                 "Median": vals["median"]})
            if rows:
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        # Distribution charts
        for chart in comparison.get("distribution_charts", []):
            st.plotly_chart(chart["fig"], use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# TAB 7 — BIAS REPORT
# ════════════════════════════════════════════════════════════════════════════
with t7:
    st.markdown("### ⚖️ Bias & Fairness Report Card")
    st.markdown(
        "DataForge audits your dataset for potential bias issues — "
        "skewness, class imbalance, proxy variables and representation gaps. "
        "This is essential before deploying any ML model."
    )

    # Target column selector for imbalance check
    bias_target = st.selectbox(
        "Select target column to check for class imbalance (optional):",
        options=["None"] + cleaned.columns.tolist(),
        key="bias_target"
    )
    target_col = None if bias_target == "None" else bias_target

    if st.button("🔍 Run Bias Audit", key="bias_btn"):
        with st.spinner("Running comprehensive bias audit..."):
            bias_report = run_bias_audit(cleaned, target_col=target_col)
        st.session_state["bias_report"] = bias_report

    if "bias_report" in st.session_state:
        render_bias_report(st, st.session_state["bias_report"])

        # Voice narration of risk summary
        risk  = st.session_state["bias_report"]["overall_risk"]
        grade = st.session_state["bias_report"]["grade"]
        recs  = st.session_state["bias_report"].get("recommendations", [])
        bias_summary = (
            f"Your dataset received a bias risk grade of {grade}. "
            f"Overall risk level is {risk}. "
            + " ".join(recs[:2])
        )
        speak(bias_summary, label="Listen to Bias Summary", key_suffix="bias_summary")

        # Educational note
        st.markdown("### 📖 Why Bias Matters")
        bias_lesson = (
            "**Data bias** occurs when a dataset does not fairly represent the real world. "
            "If a model is trained on biased data, its predictions will also be biased — "
            "which can cause real harm when used in hiring, lending, healthcare or education. "
            "The EU AI Act requires organisations to document and mitigate bias before "
            "deploying AI systems. DataForge flags these issues so you can address them early."
        )
        lesson_box(bias_lesson)
        speak(bias_lesson, label="Listen to Bias Lesson", key_suffix="bias_lesson")

# ════════════════════════════════════════════════════════════════════════════
# TAB 8 — COLLABORATE
# ════════════════════════════════════════════════════════════════════════════
with t8:
    import json as _json

    COLLAB_FILE = "collab_sessions.json"

    def _load_sessions():
        if os.path.exists(COLLAB_FILE):
            with open(COLLAB_FILE) as f:
                return _json.load(f)
        return {}

    def _save_sessions(s):
        with open(COLLAB_FILE, "w") as f:
            _json.dump(s, f, indent=2)

    st.markdown("### 🤝 Collaborative Mode")
    st.markdown("Work on the same dataset with classmates — share findings, "
                "compare quiz scores, and chat in real time.")

    # Room setup
    st.markdown("#### Join or Create a Room")
    col_n, col_r = st.columns(2)
    with col_n:
        collab_name = st.text_input("Your name", placeholder="Enter your name...",
                                     key="collab_name_input")
    with col_r:
        room_code = st.text_input("Room code", placeholder="e.g. DS2026A",
                                   key="collab_room_input").upper().strip()

    col_c, col_j = st.columns(2)
    with col_c:
        if st.button("➕ Create Room", key="create_room"):
            if collab_name and room_code:
                sessions = _load_sessions()
                if room_code not in sessions:
                    sessions[room_code] = {
                        "members": [collab_name],
                        "messages": [],
                        "scores": {collab_name: st.session_state["score"]},
                        "created": str(pd.Timestamp.now()),
                    }
                    _save_sessions(sessions)
                st.session_state["collab_room"]  = room_code
                st.session_state["collab_member"] = collab_name
                st.success(f"Room **{room_code}** created! Share this code with classmates.")
            else:
                st.warning("Enter your name and a room code first.")

    with col_j:
        if st.button("🚪 Join Room", key="join_room"):
            if collab_name and room_code:
                sessions = _load_sessions()
                if room_code in sessions:
                    if collab_name not in sessions[room_code]["members"]:
                        sessions[room_code]["members"].append(collab_name)
                    sessions[room_code]["scores"][collab_name] = st.session_state["score"]
                    _save_sessions(sessions)
                    st.session_state["collab_room"]  = room_code
                    st.session_state["collab_member"] = collab_name
                    st.success(f"Joined room **{room_code}**!")
                else:
                    st.error("Room not found. Check the code or create a new one.")
            else:
                st.warning("Enter your name and the room code first.")

    # Show room content if in a room
    active_room   = st.session_state.get("collab_room")
    active_member = st.session_state.get("collab_member")

    if active_room and active_member:
        sessions = _load_sessions()
        if active_room in sessions:
            session = sessions[active_room]
            # Update this member's score
            session["scores"][active_member] = st.session_state["score"]
            _save_sessions(sessions)

            st.divider()
            st.markdown(f"**Room: `{active_room}`** · "
                        f"{len(session['members'])} member(s) joined")

            col_lb, col_chat = st.columns([1, 2])

            # Leaderboard
            with col_lb:
                st.markdown("#### 🏆 Leaderboard")
                medals = ["🥇","🥈","🥉"]
                scores = session.get("scores", {})
                sorted_scores = sorted(scores.items(),
                                       key=lambda x: x[1], reverse=True)
                for i, (member, pts) in enumerate(sorted_scores):
                    medal   = medals[i] if i < 3 else f"{i+1}."
                    you_tag = " ← you" if member == active_member else ""
                    st.markdown(
                        f"{medal} **{member}{you_tag}** — {pts} pts"
                    )

            # Chat
            with col_chat:
                st.markdown("#### 💬 Class Chat")
                messages = session.get("messages", [])
                chat_area = st.container()
                with chat_area:
                    for msg in messages[-15:]:
                        you = " (you)" if msg["name"] == active_member else ""
                        st.markdown(
                            f'<div style="background:#161B22;border-left:3px solid #028090;'
                            f'padding:6px 12px;margin:3px 0;border-radius:0 6px 6px 0;'
                            f'font-size:.9rem;color:#E6EDF3">'
                            f'<strong style="color:#02C39A">{msg["name"]}{you}</strong>'
                            f' <span style="color:#475569;font-size:.8rem">{msg.get("time","")}</span>'
                            f'<br>{msg["text"]}</div>',
                            unsafe_allow_html=True
                        )

                msg_col1, msg_col2 = st.columns([4, 1])
                with msg_col1:
                    new_msg = st.text_input("Message",
                                             placeholder="Share a finding with your class...",
                                             key="collab_msg",
                                             label_visibility="collapsed")
                with msg_col2:
                    if st.button("Send", key="send_collab"):
                        if new_msg.strip():
                            sessions = _load_sessions()
                            sessions[active_room]["messages"].append({
                                "name": active_member,
                                "text": new_msg,
                                "time": pd.Timestamp.now().strftime("%H:%M"),
                            })
                            _save_sessions(sessions)
                            st.rerun()

            if st.button("🔄 Refresh", key="refresh_collab"):
                st.rerun()
            st.caption("Click Refresh to see latest messages and scores.")

            if st.button("🚪 Leave Room", key="leave_room"):
                st.session_state.pop("collab_room", None)
                st.session_state.pop("collab_member", None)
                st.rerun()

# ── Final score ────────────────────────────────────────────────────────────
st.divider()
completed_count = len(set(st.session_state["steps_completed"]))
pct = int((completed_count / 6) * 100)
st.markdown(f"### 🎓 Your Learning Progress: {pct}% complete")
st.progress(pct / 100)
score = st.session_state["score"]
if score > 0:
    grade_msg = "Outstanding! 🌟" if score >= 60 else "Great work! 💪" if score >= 30 else "Good start! 📚"
    st.markdown(f"🏆 **Quiz Score: {score} points** — {grade_msg}")

# ── Certificate section ────────────────────────────────────────────────────
st.divider()
st.markdown("### 🎓 Your Certificate")
steps_done = list(set(st.session_state["steps_completed"]))
quiz_total = len([k for k in st.session_state["quiz_answers"]]) * 10

show_certificate_section(
    st=st,
    student_name=st.session_state.get("student_name", ""),
    score=st.session_state["score"],
    total=max(quiz_total, 10),
    level=level,
    dataset_name=getattr(df_raw, "name", "your dataset") if df_raw is not None else "your dataset",
    steps_completed=steps_done,
)

# Speak congratulations when all done
if len(steps_done) >= 6 and st.session_state["score"] >= 5:
    speak(get_narration("certificate"),
          label="🏆 Hear Your Congratulations", key_suffix="cert_narration")