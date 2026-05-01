# agents/theme_toggle.py
import streamlit as st
import json
import os

THEME_FILE = "data/themes.json"


def _load_themes():
    os.makedirs("data", exist_ok=True)
    if os.path.exists(THEME_FILE):
        with open(THEME_FILE) as f:
            return json.load(f)
    return {}


def _save_themes(themes):
    os.makedirs("data", exist_ok=True)
    with open(THEME_FILE, "w") as f:
        json.dump(themes, f, indent=2)


def get_user_theme(username=""):
    if not username:
        return "dark"
    themes = _load_themes()
    return themes.get(username, "dark")


def save_user_theme(username, theme):
    themes = _load_themes()
    themes[username] = theme
    _save_themes(themes)


def apply_theme(theme):
    if theme == "light":
        st.markdown("""
        <style>
        * { transition: background-color 0.3s ease, color 0.3s ease !important; }
        .stApp { background-color:#F8FAFC !important; color:#1E293B !important; }
        section[data-testid="stSidebar"] { background-color:#F1F5F9 !important; }
        section[data-testid="stSidebar"] * { color:#1E293B !important; }
        .lesson-box { background:#EFF6FF !important; color:#1E293B !important; }
        .metric-card { background:#FFFFFF !important; border:1px solid #CBD5E1 !important; }
        .metric-val { color:#028090 !important; }
        .quiz-box { background:#F0F9FF !important; }
        .audit-entry { background:#F8FAFC !important; color:#374151 !important; }
        .chat-user { background:#E0F2FE !important; color:#1E293B !important; }
        .chat-tutor { background:#FFFFFF !important; color:#1E293B !important; }
        .stButton>button { background-color:#028090 !important; color:white !important; }
        .stTabs [aria-selected="true"] { color:#028090 !important; border-bottom-color:#028090 !important; }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        * { transition: background-color 0.3s ease, color 0.3s ease !important; }
        .stApp { background-color:#0D1117 !important; color:#F0F6FC !important; }
        section[data-testid="stSidebar"] { background-color:#161B22 !important; }
        section[data-testid="stSidebar"] * { color:#F0F6FC !important; }
        .lesson-box { background:#161B22 !important; color:#E6EDF3 !important; }
        .metric-card { background:#161B22 !important; border:1px solid #028090 !important; }
        .metric-val { color:#02C39A !important; }
        .quiz-box { background:#0D2137 !important; }
        .audit-entry { background:#161B22 !important; color:#C9D1D9 !important; }
        .chat-user { background:#1C2333 !important; color:#E6EDF3 !important; }
        .chat-tutor { background:#161B22 !important; color:#E6EDF3 !important; }
        .stButton>button { background-color:#02C39A !important; color:#0D1117 !important; }
        .stTabs [aria-selected="true"] { color:#02C39A !important; border-bottom-color:#02C39A !important; }
        </style>
        """, unsafe_allow_html=True)


def render_theme_toggle(username=""):
    saved_theme = get_user_theme(username)
    if "theme" not in st.session_state:
        st.session_state["theme"] = saved_theme

    current = st.session_state["theme"]
    icon    = "☀️" if current == "dark" else "🌙"
    label   = f"{icon} Switch to {'Light' if current == 'dark' else 'Dark'} Mode"

    if st.button(label, key="theme_toggle_btn"):
        new_theme = "light" if current == "dark" else "dark"
        st.session_state["theme"] = new_theme
        if username:
            save_user_theme(username, new_theme)
        st.rerun()

    apply_theme(st.session_state["theme"])
    return st.session_state["theme"]
