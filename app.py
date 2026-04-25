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
from agents.intent_router    import route_intent, validate_task
from agents.chat_orchestrator import run_selected_agents
from login_page        import render_login_page, render_logout_button
from challenge_tab     import render_challenge_tab
from progress_tab      import render_progress_tab
from agents.theme_toggle   import render_theme_toggle
from agents.dataset_history import (save_dataset_session, generate_dataset_summary,
                                     render_conversation_history, render_dataset_history)
from agents.glossary       import render_glossary_tab
from agents.eda_tools      import (explain_chart_gpt, explain_chart_local,
                                    generate_eda_story_gpt, generate_eda_story_local,
                                    generate_diff_view, render_diff_view,
                                    build_export_pack)
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

# ── Anime mascot SVG ──────────────────────────────────────────────────────
MASCOT_SVG = """
<svg width="64" height="64" viewBox="0 0 72 72" fill="none" xmlns="http://www.w3.org/2000/svg">
  <ellipse cx="36" cy="32" rx="18" ry="19" fill="#E6F1FB"/>
  <path d="M18 28 Q16 14 28 12 Q36 8 44 12 Q56 14 54 28" fill="#185FA5"/>
  <path d="M18 28 Q14 20 20 16" stroke="#185FA5" stroke-width="3" stroke-linecap="round"/>
  <path d="M54 28 Q58 20 52 16" stroke="#185FA5" stroke-width="3" stroke-linecap="round"/>
  <path d="M26 10 Q28 4 32 8" fill="#185FA5"/>
  <path d="M36 8 Q38 2 42 6" fill="#185FA5"/>
  <ellipse cx="28" cy="31" rx="5" ry="6" fill="white"/>
  <ellipse cx="44" cy="31" rx="5" ry="6" fill="white"/>
  <circle cx="29" cy="32" r="3.5" fill="#185FA5"/>
  <circle cx="45" cy="32" r="3.5" fill="#185FA5"/>
  <circle cx="30" cy="31" r="1.2" fill="white"/>
  <circle cx="46" cy="31" r="1.2" fill="white"/>
  <path d="M23 27 Q25 25 27 27" stroke="#185FA5" stroke-width="1" fill="none" stroke-linecap="round"/>
  <path d="M41 27 Q43 25 45 27" stroke="#185FA5" stroke-width="1" fill="none" stroke-linecap="round"/>
  <ellipse cx="21" cy="37" rx="4" ry="2.5" fill="#F4C0D1" opacity="0.7"/>
  <ellipse cx="51" cy="37" rx="4" ry="2.5" fill="#F4C0D1" opacity="0.7"/>
  <path d="M30 40 Q36 45 42 40" stroke="#378ADD" stroke-width="1.5" fill="none" stroke-linecap="round"/>
  <rect x="30" y="18" width="12" height="7" rx="1.5" fill="#1D9E75" opacity="0.85"/>
  <rect x="31.5" y="21" width="1.5" height="3" fill="white"/>
  <rect x="34" y="19.5" width="1.5" height="4.5" fill="white"/>
  <rect x="36.5" y="20.5" width="1.5" height="3.5" fill="white"/>
  <rect x="39" y="20" width="1.5" height="4" fill="white"/>
  <ellipse cx="18" cy="32" rx="3" ry="4" fill="#E6F1FB"/>
  <ellipse cx="54" cy="32" rx="3" ry="4" fill="#E6F1FB"/>
  <path d="M18 50 Q20 44 36 43 Q52 44 54 50 L56 58 Q36 62 16 58 Z" fill="#185FA5"/>
  <path d="M30 44 L36 50 L42 44" stroke="#E6F1FB" stroke-width="1.5" fill="none"/>
  <rect x="31" y="52" width="10" height="5" rx="1" fill="#1D9E75"/>
  <text x="36" y="56.5" font-size="4.5" fill="white" text-anchor="middle" font-weight="bold" font-family="Arial">DF</text>
</svg>
"""

MASCOT_SMALL = """
<svg width="28" height="28" viewBox="0 0 72 72" fill="none">
  <ellipse cx="36" cy="32" rx="18" ry="19" fill="#E6F1FB"/>
  <path d="M18 28 Q16 14 28 12 Q36 8 44 12 Q56 14 54 28" fill="#185FA5"/>
  <ellipse cx="28" cy="31" rx="5" ry="6" fill="white"/>
  <ellipse cx="44" cy="31" rx="5" ry="6" fill="white"/>
  <circle cx="29" cy="32" r="3.5" fill="#185FA5"/>
  <circle cx="45" cy="32" r="3.5" fill="#185FA5"/>
  <circle cx="30" cy="31" r="1.2" fill="white"/>
  <circle cx="46" cy="31" r="1.2" fill="white"/>
  <ellipse cx="21" cy="37" rx="4" ry="2.5" fill="#F4C0D1" opacity="0.7"/>
  <ellipse cx="51" cy="37" rx="4" ry="2.5" fill="#F4C0D1" opacity="0.7"/>
  <path d="M30 40 Q36 45 42 40" stroke="#378ADD" stroke-width="1.5" fill="none" stroke-linecap="round"/>
  <path d="M18 50 Q20 44 36 43 Q52 44 54 50 L56 58 Q36 62 16 58 Z" fill="#185FA5"/>
</svg>
"""

# ── CSS ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Base ── */
    .stApp { background-color:#0D1117; color:#F0F6FC; }
    section[data-testid="stSidebar"] { background-color:#0D1117; border-right:1px solid #1E293B; }
    section[data-testid="stSidebar"] * { color:#F0F6FC !important; }
    #MainMenu{visibility:hidden} footer{visibility:hidden}

    /* ── Mascot header ── */
    .df-header {
        display:flex; align-items:center; gap:12px;
        padding:1rem 0 0.5rem;
    }
    .df-header-text h1 {
        font-size:1.6rem; font-weight:800; color:#02C39A;
        margin:0; line-height:1.2;
    }
    .df-header-text p {
        font-size:0.82rem; color:#8B949E; margin:0;
    }

    /* ── Chat bubbles ── */
    .chat-wrap   { overflow:hidden; margin-bottom:0.6rem; }
    .chat-user   {
        background:#185FA5; border-radius:18px 18px 4px 18px;
        padding:0.75rem 1rem; margin:0.3rem 0; color:white;
        max-width:78%; float:right; clear:both;
        font-size:0.93rem; line-height:1.6;
    }
    .chat-tutor  {
        background:#161B22; border:1px solid #1E293B;
        border-radius:4px 18px 18px 18px;
        padding:0.75rem 1rem; margin:0.3rem 0; color:#E6EDF3;
        max-width:82%; float:left; clear:both;
        font-size:0.93rem; line-height:1.6;
    }
    .chat-bot-row {
        display:flex; align-items:flex-start; gap:8px; margin:0.3rem 0; clear:both;
    }
    .chat-bot-avatar {
        flex-shrink:0; margin-top:2px;
    }
    .chat-user-label {
        float:right; clear:both;
        font-size:0.72rem; color:#8B949E;
        margin-bottom:2px; margin-right:4px;
    }

    /* ── Cards and components ── */
    .lesson-box {
        background:#111827; border-left:3px solid #02C39A;
        border-radius:0 12px 12px 0; padding:1.1rem 1.4rem;
        margin:0.7rem 0; color:#E6EDF3; line-height:1.85;
        font-size:0.93rem;
    }
    .metric-card {
        background:#111827; border:1px solid #1E293B;
        border-radius:12px; padding:.85rem 1rem;
        transition: border-color 0.2s;
    }
    .metric-card:hover { border-color:#028090; }
    .metric-val  { font-size:1.7rem; font-weight:800; color:#02C39A; }
    .metric-lbl  { font-size:.78rem; color:#8B949E; margin-top:2px; }

    .step-badge {
        background:#028090; color:white; border-radius:20px;
        padding:3px 14px; font-size:0.82rem; font-weight:700;
        display:inline-block; margin-bottom:8px; letter-spacing:0.3px;
    }

    /* ── Quiz ── */
    .quiz-box {
        background:#111827; border:1px solid #1E293B;
        border-radius:12px; padding:1.1rem; margin:0.7rem 0;
    }
    .quiz-q { font-size:0.95rem; font-weight:700; color:#E6EDF3; margin-bottom:0.7rem; }
    .correct {
        background:#052e16; border:1px solid #166534;
        border-radius:10px; padding:0.6rem 1rem;
        color:#86EFAC; font-weight:600; font-size:0.9rem;
    }
    .wrong {
        background:#2d0a0a; border:1px solid #7F1D1D;
        border-radius:10px; padding:0.6rem 1rem;
        color:#FCA5A5; font-weight:600; font-size:0.9rem;
    }
    .explanation {
        background:#1a2234; border-radius:10px; padding:0.75rem 1rem;
        color:#94A3B8; font-size:0.88rem; margin-top:0.5rem;
        line-height:1.7;
    }

    /* ── Audit trail ── */
    .audit-entry {
        background:#111827; border-left:2px solid #028090;
        padding:5px 12px; margin:3px 0; border-radius:0 8px 8px 0;
        font-size:.82rem; font-family:monospace; color:#94A3B8;
    }

    /* ── AutoML ── */
    .automl-best {
        background:linear-gradient(135deg,#0f4c6e,#0a6e56);
        border:1px solid #02C39A;
        border-radius:12px; padding:1rem; color:white; text-align:center;
    }
    .automl-score { font-size:1.9rem; font-weight:900; }

    /* ── Buttons ── */
    .stButton>button {
        background-color:#02C39A; color:#0D1117;
        font-weight:700; border:none; border-radius:10px;
        padding:0.45rem 1.2rem; transition: all 0.2s;
    }
    .stButton>button:hover {
        background-color:#01a882; color:white;
        transform: translateY(-1px);
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab"] {
        color:#8B949E; font-size:0.88rem;
        padding:0.5rem 0.8rem;
    }
    .stTabs [aria-selected="true"] {
        color:#02C39A !important;
        border-bottom-color:#02C39A !important;
        font-weight:600;
    }

    /* ── Suggestion chips ── */
    .sug-chip {
        display:inline-block; padding:5px 14px;
        background:#111827; border:1px solid #1E293B;
        border-radius:20px; font-size:0.82rem; color:#8B949E;
        margin:3px; cursor:pointer; transition:all 0.15s;
    }
    .sug-chip:hover {
        background:#185FA5; border-color:#185FA5; color:white;
    }

    /* ── Input area ── */
    .stTextInput>div>div>input {
        border-radius:12px !important;
        border-color:#1E293B !important;
        background:#111827 !important;
        color:#F0F6FC !important;
        padding:0.6rem 1rem !important;
    }
    .stTextInput>div>div>input:focus {
        border-color:#028090 !important;
        box-shadow: 0 0 0 2px rgba(2,128,144,0.15) !important;
    }

    /* ── Agent badges ── */
    .agent-badge {
        display:inline-block; padding:2px 10px;
        background:#052e16; border:1px solid #166534;
        border-radius:20px; font-size:0.75rem; color:#86EFAC;
        font-weight:600; margin:2px;
    }
    .declined-badge {
        display:inline-block; padding:2px 10px;
        background:#2d0a0a; border:1px solid #7F1D1D;
        border-radius:20px; font-size:0.75rem; color:#FCA5A5;
        font-weight:600; margin:2px;
    }

    /* ── Tutor sub-header ── */
    .tutor-title { font-size:2.2rem; font-weight:900; color:#02C39A; margin-bottom:0; }
    .tutor-sub   { font-size:0.9rem; color:#8B949E; margin-top:2px; font-style:italic; }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────
for key, default in [
    ("level", "beginner"), ("chat_history", []),
    ("quiz_answers", {}),  ("steps_completed", []), ("score", 0),
    ("app_mode", "chat"),  ("chat_messages", []),
    ("df_raw_chat", None), ("cleaned_df_chat", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Authentication gate ───────────────────────────────────────────────────
render_login_page()
username = st.session_state.get("username", "")

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
    st.markdown(
        f'<div style="text-align:center;padding:0.5rem 0 0.8rem">'
        f'{MASCOT_SVG}'
        f'<div style="font-size:1.1rem;font-weight:800;color:#02C39A;margin-top:6px">DataForge</div>'
        f'<div style="font-size:0.75rem;color:#8B949E">AI Data Science Tutor</div>'
        f'</div>',
        unsafe_allow_html=True)
    st.divider()

    # ── Mode toggle ────────────────────────────────────────────────────
    st.markdown("### 🔀 Mode")
    mode = st.radio(
        "Choose how you want to use DataForge:",
        ["💬 Chat Mode (recommended)", "⚡ Pipeline Mode (run everything)"],
        index=0 if st.session_state["app_mode"] == "chat" else 1,
        key="mode_radio"
    )
    st.session_state["app_mode"] = "chat" if "Chat" in mode else "pipeline"
    if st.session_state["app_mode"] == "chat":
        st.caption("Tell DataForge what you want — agents run on demand")
    else:
        st.caption("Upload a file and run the full pipeline in one click")
    st.divider()

    # ── AI status ──────────────────────────────────────────────────────
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

    # ── Level selector ─────────────────────────────────────────────────
    st.markdown("### 📚 Your Level")
    level_pick = st.radio(
        "Choose your level:",
        ["Beginner", "Intermediate"],
        index=0 if st.session_state["level"] == "beginner" else 1
    )
    st.session_state["level"] = level_pick.lower()
    st.divider()

    # ── Progress (pipeline mode only) ──────────────────────────────────
    if st.session_state["app_mode"] == "pipeline":
        st.markdown("### 📊 Your Progress")
        done_steps = [s.lower() for s in st.session_state["steps_completed"]]
        for step in ["Upload", "Clean", "Analyse", "Visualise", "AutoML", "Chat"]:
            icon = "✅" if step.lower() in done_steps else "⭕"
            st.markdown(f"{icon} {step}")
        st.divider()
        st.markdown(f"### 🏆 Quiz Score: {st.session_state['score']} pts")
        st.progress(len(set(done_steps)) / 6)
        st.caption(f"{len(set(done_steps))}/6 steps complete")
        st.divider()

    # ── Student name ───────────────────────────────────────────────────
    st.markdown("### 👤 Your Name")
    st.text_input("Name (for certificate)", placeholder="Enter your name...",
                  key="student_name")
    st.divider()

    # ── Theme toggle ────────────────────────────────────────────────────
    st.markdown("### 🎨 Theme")
    render_theme_toggle(username=st.session_state.get("username", ""))
    st.divider()

    # ── Voice ──────────────────────────────────────────────────────────
    st.markdown("### 🔊 Voice Narration")
    if use_gpt:
        st.caption("Click 🔊 Listen buttons to hear lessons aloud")
    else:
        st.caption("Add OPENAI_API_KEY to .env to enable voice")

    # ── Clear chat ──────────────────────────────────────────────────────
    if st.session_state["app_mode"] == "chat":
        st.divider()
        if st.button("🗑️ Clear conversation"):
            st.session_state["chat_messages"]   = []
            st.session_state["df_raw_chat"]     = None
            st.session_state["cleaned_df_chat"] = None
            st.rerun()



# ══════════════════════════════════════════════════════════════════════════
# CHAT MODE — conversational interface (main entry point)
# ══════════════════════════════════════════════════════════════════════════
def _render_chat_mode(level, use_gpt, gpt_client, use_live):
    """Renders the full conversational chatbot interface."""

    # ── Upload section ─────────────────────────────────────────────────
    # ── Upload header ─────────────────────────────────────────────────
    st.markdown(
        '<div style="background:#111827;border:1.5px dashed #028090;'
        'border-radius:14px;padding:1.2rem 1.5rem;margin-bottom:1rem">'
        '<div style="font-size:1rem;font-weight:700;color:#02C39A;margin-bottom:4px">'
        '📂 Upload Your Dataset</div>'
        '<div style="font-size:0.82rem;color:#8B949E">'
        'CSV or Excel · any domain · up to 200MB</div>'
        '</div>',
        unsafe_allow_html=True)
    col_up1, col_up2 = st.columns([2, 1])
    with col_up1:
        uploaded_chat = st.file_uploader(
            "Drop your file here",
            type=["csv", "xlsx", "xls"], key="chat_uploader",
            label_visibility="collapsed")
    with col_up2:
        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
        use_demo_chat = st.checkbox("🎯 Use demo dataset", key="chat_demo")

    if use_demo_chat:
        rng = np.random.default_rng(42)
        n   = 400
        df_chat = pd.DataFrame({
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
        df_chat.loc[idx, "age"]         = None
        df_chat.loc[idx[:10], "income"] = None
        df_chat = pd.concat([df_chat, df_chat.iloc[:15]], ignore_index=True)
        if st.session_state.get("df_raw_chat") is None:
            st.session_state["df_raw_chat"] = df_chat
            st.session_state["chat_messages"] = []
        st.success(f"Demo dataset ready: {df_chat.shape[0]} rows × {df_chat.shape[1]} columns")

    elif uploaded_chat:
        try:
            df_chat = (pd.read_csv(uploaded_chat)
                       if uploaded_chat.name.endswith(".csv")
                       else pd.read_excel(uploaded_chat))
            if st.session_state.get("df_raw_chat") is None or                st.session_state.get("_chat_fname") != uploaded_chat.name:
                st.session_state["df_raw_chat"]  = df_chat
                st.session_state["_chat_fname"]  = uploaded_chat.name
                st.session_state["chat_messages"] = []
            st.success(f"✅ {uploaded_chat.name} — "
                       f"{df_chat.shape[0]:,} rows × {df_chat.shape[1]} columns")
        except Exception as e:
            st.error(f"Failed to read file: {e}")

    df_raw = st.session_state.get("df_raw_chat")

    # ── No dataset yet ─────────────────────────────────────────────────
    if df_raw is None:
        st.info("👆 Upload a dataset or tick the demo checkbox above to get started.")
        st.markdown("""
**Then tell DataForge what you want, for example:**
- *"Clean my data and show me the statistics"*
- *"Find correlations and create interactive charts"*
- *"Train a machine learning model to predict churn"*
- *"Run a full analysis and write a report"*
- *"Check my data for bias and fairness issues"*
        """)
        return

    # ── Dataset info ───────────────────────────────────────────────────
    k1, k2, k3 = st.columns(3)
    for col_st, val, lbl in [
        (k1, f"{df_raw.shape[0]:,}", "Rows"),
        (k2, df_raw.shape[1], "Columns"),
        (k3, len(df_raw.select_dtypes(include=["number"]).columns), "Numeric cols"),
    ]:
        col_st.markdown(
            f'<div class="metric-card"><div class="metric-val">{val}</div>'
            f'<div class="metric-lbl">{lbl}</div></div>',
            unsafe_allow_html=True)

    st.divider()

    # ── Suggested prompts (shown only when conversation is empty) ──────
    if not st.session_state["chat_messages"]:
        st.markdown("**💡 Try asking:**")
        suggestions = [
            "Clean my data and show me the statistics",
            "Find correlations and visualise my data",
            "Predict a column using machine learning",
            "Write a full analysis report",
            "Check my data for bias and fairness issues",
            "Run a complete data science pipeline",
        ]
        scols = st.columns(3)
        for i, sug in enumerate(suggestions):
            with scols[i % 3]:
                if st.button(sug, key=f"chatsugg_{i}", width="stretch"):
                    st.session_state["_pending_msg"] = sug
                    st.rerun()
        st.divider()

    # ── Render conversation history ────────────────────────────────────
    for msg_idx, msg in enumerate(st.session_state["chat_messages"]):

        if msg["role"] == "user":
            st.markdown(
                f'<div class="chat-wrap">'
                f'<div class="chat-user-label">You</div>'
                f'<div class="chat-user">{msg["text"]}</div>'
                f'</div>',
                unsafe_allow_html=True)

        elif msg["role"] == "bot":
            st.markdown(
                f'<div class="chat-bot-row">'
                f'<div class="chat-bot-avatar">{MASCOT_SMALL}</div>'
                f'<div class="chat-tutor">{msg["text"]}</div>'
                f'</div>',
                unsafe_allow_html=True)

            # Agent badges
            if msg.get("agents_ran"):
                badges = " ".join(
                    f'<span style="background:#028090;color:white;border-radius:20px;'
                    f'padding:2px 10px;font-size:.78rem;font-weight:bold;margin:2px">'
                    f'✅ {a.title()}</span>'
                    for a in msg["agents_ran"]
                )
                if msg.get("agents_declined"):
                    badges += " " + " ".join(
                        f'<span style="background:#7F1D1D;color:#FCA5A5;'
                        f'border-radius:20px;padding:2px 10px;font-size:.78rem;'
                        f'font-weight:bold;margin:2px">❌ {a}</span>'
                        for a in msg["agents_declined"]
                    )
                st.markdown(badges, unsafe_allow_html=True)

            results  = msg.get("results")
            teaching = msg.get("teaching_focus", "data science")

            # ── Personalised lesson ─────────────────────────────────
            if results and results.get("success"):
                lesson_key = f"chat_lesson_{msg_idx}"
                if lesson_key not in st.session_state:
                    df_c     = results.get("cleaned_df", df_raw)
                    insights = results.get("insights", {})
                    audit    = results.get("audit_log", [])
                    if use_gpt and gpt_client and df_c is not None:
                        try:
                            from agents.gpt_tutor import generate_lesson, build_dataset_context
                            ctx = build_dataset_context(df_c, insights, audit)
                            st.session_state[lesson_key] = generate_lesson(
                                gpt_client, teaching, level, ctx)
                        except Exception:
                            st.session_state[lesson_key] = get_lesson(
                                teaching, "intro", level)
                    else:
                        st.session_state[lesson_key] = get_lesson(
                            teaching, "intro", level)

                lesson_text = st.session_state.get(lesson_key, "")
                if lesson_text:
                    with st.expander("📖 What this means — personalised lesson",
                                     expanded=True):
                        st.markdown(
                            f'<div class="lesson-box">{lesson_text}</div>',
                            unsafe_allow_html=True)
                        speak(lesson_text, label="Listen to lesson",
                              key_suffix=f"chl_{msg_idx}")

                # Audit trail
                audit = results.get("audit_log", [])
                if "clean" in msg.get("agents_ran", []) and audit:
                    with st.expander("🧹 Cleaning audit", expanded=False):
                        for entry in audit[:10]:
                            st.markdown(
                                f'<div class="audit-entry">{entry}</div>',
                                unsafe_allow_html=True)
                        df_c = results.get("cleaned_df")
                        if df_c is not None:
                            st.download_button(
                                "⬇️ Download cleaned CSV",
                                df_c.to_csv(index=False).encode(),
                                "cleaned_data.csv", "text/csv",
                                key=f"dl_clean_chat_{msg_idx}")

                # Statistics
                insights = results.get("insights", {})
                if "analyse" in msg.get("agents_ran", []) and insights:
                    with st.expander("📊 Statistics", expanded=True):
                        if insights.get("numeric_summary"):
                            st.dataframe(
                                pd.DataFrame(insights["numeric_summary"]).T.round(3),
                                width="stretch")
                        if insights.get("strong_correlations"):
                            st.markdown("**Correlations found:**")
                            for p in insights["strong_correlations"]:
                                d = "🟢" if p["correlation"] > 0 else "🔴"
                                st.markdown(
                                    f"- {d} **{p['col_a']}** ↔ **{p['col_b']}**: "
                                    f"r = `{p['correlation']}`")

                # Charts
                charts = results.get("charts", [])
                if "visualise" in msg.get("agents_ran", []) and charts:
                    with st.expander("📈 Charts", expanded=True):
                        for ci, chart in enumerate(charts):
                            st.markdown(f"**{chart['title']}**")
                            st.plotly_chart(chart["fig"],
                                width="stretch",
                                key=f"chat_chart_{msg_idx}_{ci}",
                                            config={"displayModeBar": True})

                # ML results
                ml_res = results.get("ml_results")
                if "automl" in msg.get("agents_ran", []) and ml_res and                         not ml_res.get("error"):
                    with st.expander("🤖 Machine learning results", expanded=True):
                        best   = ml_res.get("best_model", "Unknown")
                        score  = ml_res.get("best_score", 0)
                        metric = ml_res.get("best_metric", "accuracy")
                        st.markdown(
                            f'<div class="automl-best">'
                            f'<div class="automl-score">{best}</div>'
                            f'<div>{metric}: {score:.1%}</div></div>',
                            unsafe_allow_html=True)
                        if ml_res.get("models"):
                            mdf = pd.DataFrame(ml_res["models"])
                            st.dataframe(
                                mdf.style.background_gradient(
                                    subset=["score"], cmap="YlGn"),
                                width="stretch")
                        if ml_res.get("feature_importance"):
                            import plotly.express as px
                            fi_df = pd.DataFrame(
                                list(ml_res["feature_importance"].items()),
                                columns=["Feature", "Importance"])
                            fig = px.bar(
                                fi_df, x="Importance", y="Feature",
                                orientation="h", color="Importance",
                                color_continuous_scale=["#028090","#02C39A"])
                            fig.update_layout(
                                plot_bgcolor="white", paper_bgcolor="white",
                                showlegend=False, coloraxis_showscale=False,
                                yaxis=dict(autorange="reversed"))
                            st.plotly_chart(fig, width="stretch")

                # Report
                report = results.get("report")
                if "report" in msg.get("agents_ran", []) and report:
                    with st.expander("📝 Analysis report", expanded=False):
                        st.markdown(report)
                        st.download_button(
                            "⬇️ Download report",
                            report.encode(), "dataforge_report.md",
                            "text/markdown", key=f"dl_rpt_chat_{msg_idx}")
                    speak(report[:800], label="Listen to report summary",
                          key_suffix=f"rpt_chat_{msg_idx}")

                # Bias
                bias_rep = results.get("bias_report")
                if "bias" in msg.get("agents_ran", []) and bias_rep:
                    with st.expander("⚖️ Bias report", expanded=True):
                        from agents.bias_report import render_bias_report
                        render_bias_report(st, bias_rep)

                # Resources
                if use_live:
                    with st.spinner("Finding resources..."):
                        res = fetch_live_resources(
                            teaching, level,
                            youtube_key=YOUTUBE_KEY or None,
                            tavily_key=TAVILY_KEY or None)
                else:
                    res = get_resources(teaching, level)
                vids = res.get("videos", [])[:2]
                arts = res.get("articles", [])[:2]
                if vids or arts:
                    with st.expander("📚 Learn more", expanded=False):
                        for v in vids:
                            c1, c2 = st.columns([4, 1])
                            with c1:
                                st.markdown(f"**[{v['title']}]({v['url']})**  \n"
                                            f"📺 *{v['channel']}*")
                            with c2:
                                st.link_button("▶ Watch", v["url"])
                        for a in arts:
                            c1, c2 = st.columns([4, 1])
                            with c1:
                                st.markdown(f"**[{a['title']}]({a['url']})**  \n"
                                            f"📖 *{a['source']}*")
                            with c2:
                                st.link_button("📖 Read", a["url"])

        elif msg["role"] == "error":
            st.error(msg["text"])

    # ── Chat input (always at bottom) ──────────────────────────────────
    st.divider()
    st.markdown("#### 💬 Tell DataForge what you want:")
    ci1, ci2 = st.columns([5, 1])
    with ci1:
        user_input = st.text_input(
            "Request",
            placeholder="e.g. Clean my data and find correlations  |  "
                        "Predict churn with machine learning  |  Check for bias",
            label_visibility="collapsed",
            key="chatbot_input")
    with ci2:
        send = st.button("Send ➤", key="chatbot_send", width="stretch")

    # Use a pending message flag to prevent double processing
    if send and user_input.strip():
        st.session_state["_pending_msg"] = user_input.strip()
        st.rerun()

    if st.session_state.get("_pending_msg"):
        user_msg = st.session_state.pop("_pending_msg")
        # Only add if not already last message
        msgs = st.session_state["chat_messages"]
        if not (msgs and msgs[-1].get("role") == "user" and msgs[-1].get("text") == user_msg):
            st.session_state["chat_messages"].append(
                {"role": "user", "text": user_msg})

        # Route intent via GPT-4
        with st.spinner("DataForge is thinking..."):
            routing = route_intent(user_msg, df_raw, gpt_client)

        feasible    = routing.get("feasible", True)
        agents      = routing.get("agents_to_run", ["clean", "analyse"])
        target_col  = routing.get("target_col")
        decline_msg = routing.get("decline_reason", "")
        plan        = routing.get("response_plan", "")
        teaching    = routing.get("teaching_focus", "data science")

        if not feasible:
            # Agent declines the task — explains why
            st.session_state["chat_messages"].append({
                "role": "bot",
                "text": f"I cannot do that with this dataset.\n\n"
                        f"{decline_msg}\n\n{plan}",
                "agents_ran":      [],
                "agents_declined": agents,
                "results":         None,
                "teaching_focus":  teaching,
            })
            st.rerun()

        # Validate each agent against actual data
        validation   = validate_task(agents, df_raw,
                                      target_col=target_col)
        valid_agents = [a for a, v in validation.items() if v["can_run"]]
        bad_agents   = {a: v["reason"] for a, v in validation.items()
                        if not v["can_run"]}

        if not valid_agents:
            reasons = " | ".join(bad_agents.values())
            st.session_state["chat_messages"].append({
                "role": "error",
                "text": f"Cannot run the requested agents: {reasons}"
            })
            st.rerun()

        # Run valid agents
        with st.spinner(f"Running {', '.join(valid_agents)}..."):
            results = run_selected_agents(
                df_raw        = df_raw,
                agents_to_run = valid_agents,
                target_col    = target_col,
                use_gpt       = use_gpt,
                gpt_client    = gpt_client,
            )

        if not results["success"]:
            st.session_state["chat_messages"].append({
                "role":  "error",
                "text":  f"Something went wrong: {results['error']}"
            })
            st.rerun()

        if results.get("cleaned_df") is not None:
            st.session_state["cleaned_df_chat"] = results["cleaned_df"]

        bot_intro = plan
        if bad_agents:
            bot_intro += "\n\n⚠️ Some tasks were skipped:\n"
            for a, reason in bad_agents.items():
                bot_intro += f"- **{a}**: {reason}\n"

        agents_ran = results.get("agents_ran", [])
        elapsed    = results.get("elapsed", 0)
        st.session_state["chat_messages"].append({
            "role":            "bot",
            "text":            (f"{bot_intro}\n\n"
                                f"✅ Done in {elapsed}s — "
                                f"ran: {', '.join(agents_ran)}."),
            "agents_ran":      agents_ran,
            "agents_declined": list(bad_agents.keys()),
            "results":         results,
            "teaching_focus":  teaching,
        })
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════
st.markdown(
    f'<div class="df-header">'
    f'{MASCOT_SVG}'
    f'<div class="df-header-text">'
    f'<h1>DataForge</h1>'
    f'<p>Your AI data science tutor — upload a dataset and tell me what you want to learn</p>'
    f'</div></div>',
    unsafe_allow_html=True)
st.divider()

level    = st.session_state["level"]
app_mode = st.session_state.get("app_mode", "chat")

# ══════════════════════════════════════════════════════════════════════════
# ROUTE: CHAT MODE (default) or PIPELINE MODE
# ══════════════════════════════════════════════════════════════════════════
if app_mode == "chat":
    _render_chat_mode(level, use_gpt, gpt_client, use_live)
    st.stop()

# ── Below here = Pipeline Mode only ──────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════
# WELCOME SCREEN (pipeline mode)
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
        st.dataframe(df_raw.head(10), width="stretch")
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
        # Save dataset session to history
        if st.session_state.get("username"):
            with st.spinner("Saving session..."):
                ai_sum = generate_dataset_summary(
                    gpt_client, df_raw,
                    results.get("insights", {}),
                    results.get("audit_log", [])
                )
                key_findings = []
                insights_r = results.get("insights", {})
                if insights_r.get("strong_correlations"):
                    for p in insights_r["strong_correlations"][:2]:
                        key_findings.append(
                            f"Strong {'positive' if p['correlation']>0 else 'negative'} "
                            f"correlation between {p['col_a']} and {p['col_b']} "
                            f"(r={p['correlation']})"
                        )
                if insights_r.get("skewed_columns"):
                    key_findings.append(
                        f"Skewed columns: {', '.join(list(insights_r['skewed_columns'].keys())[:3])}"
                    )
                save_dataset_session(
                    username     = st.session_state["username"],
                    dataset_name = getattr(uploaded, "name", "demo_dataset.csv") if not use_demo else "demo_dataset.csv",
                    shape        = df_raw.shape,
                    key_findings = key_findings,
                    ai_summary   = ai_sum,
                )
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
# Logout button
render_logout_button()

t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12, t13 = st.tabs([
    "🧹 Cleaning", "📊 Analysis", "📈 Visualisation",
    "🤖 AutoML", "💬 Ask the Tutor", "📝 Report",
    "⚖️ Bias Report", "🤝 Collaborate",
    "🧠 Challenge Me", "📈 My Progress",
    "📖 Glossary", "💬 Conversation History", "📂 Dataset History",
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
    st.dataframe(cleaned, width="stretch")
    st.download_button("⬇️ Download Cleaned CSV",
                       cleaned.to_csv(index=False).encode(),
                       "cleaned_data.csv", "text/csv")

    # ── Feature 3: Diff View ──────────────────────────────────────────
    st.divider()
    if st.button("🔄 Show Before vs After Diff", key="btn_show_diff"):
        st.session_state["show_diff"] = True
    if st.session_state.get("show_diff"):
        if "diff_data" not in st.session_state:
            st.session_state["diff_data"] = generate_diff_view(
                df_raw, cleaned, audit)
        render_diff_view(st, st.session_state["diff_data"])

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
                     width="stretch")
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
            st.plotly_chart(chart["fig"], width="stretch",
                            key=f"pipe_chart_{chart['title'].replace(' ','_')}",
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
                    speak(st.session_state[ck], label="Listen to Chart Interpretation",
                          key_suffix=f"chartinterp_{ck[:20]}")

            # ── Feature 1: Explain Chart button ──────────────────────
            explain_key = f"explain_{chart['title'].replace(' ','_')[:20]}"
            if st.button("💬 Explain This Chart", key=f"btn_{explain_key}"):
                with st.spinner("Generating plain-English explanation..."):
                    exp = explain_chart_gpt(
                        gpt_client, chart["title"],
                        chart["title"].split()[0].lower(),
                        insights, cleaned, level)
                st.session_state[explain_key] = exp
            if st.session_state.get(explain_key):
                st.markdown(
                    f'<div style="background:#0D2137;border-left:4px solid #02C39A;'
                    f'padding:1rem 1.4rem;border-radius:0 8px 8px 0;'
                    f'color:#E6EDF3;margin:.5rem 0">'
                    f'{st.session_state[explain_key]}</div>',
                    unsafe_allow_html=True)
                speak(st.session_state[explain_key],
                      label="Listen to explanation",
                      key_suffix=f"exp_{explain_key[:15]}")
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
                         width="stretch")

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
                st.plotly_chart(fig, width="stretch")

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

    # ── Feature 2: One-Click EDA Story ───────────────────────────────
    st.divider()
    st.markdown("### 📖 One-Click EDA Story")
    st.markdown("Get a plain-English narrative of your entire dataset analysis in one click.")
    if st.button("📖 Generate EDA Story", key="gen_eda_story"):
        with st.spinner("Writing your EDA story..."):
            story = generate_eda_story_gpt(
                gpt_client, df_raw, cleaned, insights, audit, level)
            st.session_state["eda_story"] = story
    if st.session_state.get("eda_story"):
        st.markdown(
            f'<div style="background:#161B22;border-left:4px solid #02C39A;'
            f'padding:1.2rem 1.5rem;border-radius:0 8px 8px 0;'
            f'color:#E6EDF3;line-height:1.8">'
            f'{st.session_state["eda_story"]}</div>',
            unsafe_allow_html=True)
        speak(st.session_state["eda_story"][:800],
              label="Listen to EDA Story", key_suffix="eda_story_audio")
        st.download_button("⬇️ Download EDA Story (.md)",
                           st.session_state["eda_story"].encode(),
                           "eda_story.md", "text/markdown",
                           key="dl_eda_story")

    st.divider()
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
                st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
        # Distribution charts
        for chart in comparison.get("distribution_charts", []):
            st.plotly_chart(chart["fig"], width="stretch")

    # ── Feature 4: Export Pack ────────────────────────────────────────
    st.divider()
    st.markdown("### 📦 Export Pack (.zip)")
    st.markdown(
        "Download everything in one zip — report, EDA story, all charts, "
        "cleaning diff, audit log, and insights JSON."
    )
    if st.button("🏗️ Build Export Pack", key="build_export"):
        with st.spinner("Building your export pack..."):
            diff_data  = st.session_state.get("diff_data") or                          generate_diff_view(df_raw, cleaned, audit)
            eda_story  = st.session_state.get("eda_story") or                          generate_eda_story_local(df_raw, cleaned, insights, audit)
            plotly_charts = results.get("charts", [])
            zip_bytes = build_export_pack(
                df_raw    = df_raw,
                cleaned_df = cleaned,
                insights   = insights,
                audit_log  = audit,
                report     = report,
                eda_story  = eda_story,
                charts     = plotly_charts,
                diff       = diff_data,
            )
            st.session_state["export_zip"] = zip_bytes
        st.success("✅ Export pack ready!")
    if st.session_state.get("export_zip"):
        st.download_button(
            "⬇️ Download Export Pack (.zip)",
            st.session_state["export_zip"],
            "dataforge_export_pack.zip",
            "application/zip",
            key="dl_export_zip",
            width="stretch",
        )


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

# ════════════════════════════════════════════════════════════════════════════
# TAB 9 — CHALLENGE ME (Socratic Mode)
# ════════════════════════════════════════════════════════════════════════════
with t9:
    if "results" not in st.session_state:
        st.info("Run the DataForge pipeline first to unlock the Challenge Me quiz.")
    else:
        render_challenge_tab(
            cleaned_df = cleaned,
            insights   = insights,
            audit_log  = audit,
            gpt_client = gpt_client,
            level      = level,
            username   = st.session_state.get("username", ""),
        )

# ════════════════════════════════════════════════════════════════════════════
# TAB 10 — MY PROGRESS
# ════════════════════════════════════════════════════════════════════════════
with t10:
    render_progress_tab(st.session_state.get("username", ""))

# ════════════════════════════════════════════════════════════════════════════
# TAB 11 — GLOSSARY
# ════════════════════════════════════════════════════════════════════════════
with t11:
    render_glossary_tab(
        username   = st.session_state.get("username", ""),
        gpt_client = gpt_client,
    )

# ════════════════════════════════════════════════════════════════════════════
# TAB 12 — CONVERSATION HISTORY
# ════════════════════════════════════════════════════════════════════════════
with t12:
    st.markdown("### 💬 Conversation History")
    st.markdown("All your interactions with the DataForge tutor this session.")
    render_conversation_history()

# ════════════════════════════════════════════════════════════════════════════
# TAB 13 — DATASET HISTORY
# ════════════════════════════════════════════════════════════════════════════
with t13:
    st.markdown("### 📂 Dataset History")
    st.markdown("All datasets you have analysed with DataForge.")
    render_dataset_history(st.session_state.get("username", ""))

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
steps_done = list(set(st.session_state["steps_completed"]))
quiz_total = len([k for k in st.session_state["quiz_answers"]]) * 10

# Celebration when all steps complete
if len(steps_done) >= 6 and st.session_state["score"] >= 5:
    st.markdown("""
    <style>
    @keyframes fall {
        0%   { transform:translateY(-20px) rotate(0deg); opacity:1; }
        100% { transform:translateY(100vh) rotate(720deg); opacity:0; }
    }
    .confetti-piece {
        position:fixed; width:10px; height:10px;
        animation:fall 3s ease-in forwards;
        pointer-events:none; z-index:9999;
    }
    </style>
    <div id="confetti-root" style="position:fixed;top:0;left:0;width:100%;height:0;pointer-events:none;z-index:9999;overflow:visible"></div>
    <script>
    (function(){
        const colors=["#02C39A","#185FA5","#F4C0D1","#FAC775","#86EFAC"];
        const root=document.getElementById("confetti-root");
        if(!root)return;
        for(let i=0;i<80;i++){
            const p=document.createElement("div");
            p.className="confetti-piece";
            p.style.left=Math.random()*100+"vw";
            p.style.top="-10px";
            p.style.background=colors[Math.floor(Math.random()*colors.length)];
            p.style.borderRadius=Math.random()>.5?"50%":"2px";
            p.style.width=(8+Math.random()*8)+"px";
            p.style.height=(8+Math.random()*8)+"px";
            p.style.animationDelay=Math.random()*1.5+"s";
            p.style.animationDuration=(2+Math.random()*2)+"s";
            root.appendChild(p);
        }
    })();
    </script>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#0a2a1e;border:1px solid #02C39A;
                border-radius:16px;padding:1.5rem;text-align:center;margin:1rem 0">
        <div style="font-size:2.8rem;margin-bottom:8px">🎓</div>
        <div style="font-size:1.5rem;font-weight:900;color:#02C39A;margin-bottom:6px">
            Pipeline Complete!
        </div>
        <div style="color:#E6EDF3;font-size:0.95rem;margin-bottom:4px">
            You have completed the full DataForge data science pipeline.
        </div>
        <div style="color:#8B949E;font-size:0.85rem">
            Your certificate is ready below ↓
        </div>
    </div>
    """, unsafe_allow_html=True)
    speak(get_narration("certificate"),
          label="🏆 Hear Your Congratulations", key_suffix="cert_narration")

st.markdown("### 🎓 Your Certificate")
show_certificate_section(
    st=st,
    student_name=st.session_state.get("student_name", ""),
    score=st.session_state["score"],
    total=max(quiz_total, 10),
    level=level,
    dataset_name=getattr(df_raw, "name", "your dataset") if df_raw is not None else "your dataset",
    steps_completed=steps_done,
)