# agents/theme_toggle.py — Upgraded Dark/Light Mode Toggle

import streamlit as st
import json
import os

THEME_FILE = "data/theme_preferences.json"

DARK_THEME = """
    <style>
        * { transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease; }
        .stApp { background-color: #0E1117 !important; color: #FAFAFA !important; }
        .stSidebar { background-color: #161B22 !important; }
        .stTextInput > div > div > input { background-color: #21262D !important; color: #FAFAFA !important; border-color: #30363D !important; }
        .stSelectbox > div > div { background-color: #21262D !important; color: #FAFAFA !important; }
        .stDataFrame { background-color: #161B22 !important; }
        .block-container { background-color: #0E1117 !important; }
        h1, h2, h3 { color: #58A6FF !important; }
        .stMetric { background-color: #161B22 !important; border-radius: 8px; padding: 10px; border: 1px solid #30363D; }
        .stAlert { border-radius: 8px; }
        .stExpander { border-color: #30363D !important; }
        p, li, label { color: #FAFAFA !important; }
        .stMarkdown { color: #FAFAFA !important; }
        .theme-badge {
            background: #58A6FF; color: #0E1117;
            padding: 4px 12px; border-radius: 20px;
            font-size: 13px; display: inline-block; margin-bottom: 10px;
        }
    </style>
"""

LIGHT_RESET = """
    <style>
        * { transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease; }
        .theme-badge {
            background: #1F3864; color: white;
            padding: 4px 12px; border-radius: 20px;
            font-size: 13px; display: inline-block; margin-bottom: 10px;
        }
    </style>
"""

SYSTEM_DETECTION_JS = """
    <script>
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const stored = window.localStorage.getItem('df_system_checked');
        if (!stored) {
            window.localStorage.setItem('df_preferred_theme', prefersDark ? 'dark' : 'light');
            window.localStorage.setItem('df_system_checked', 'true');
        }
    </script>
"""


# ── PERSISTENCE HELPERS ──

def _load_theme_prefs() -> dict:
    if not os.path.exists(THEME_FILE):
        return {}
    try:
        with open(THEME_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_theme_pref(username: str, theme: str) -> None:
    os.makedirs("data", exist_ok=True)
    prefs = _load_theme_prefs()
    prefs[username] = theme
    with open(THEME_FILE, "w") as f:
        json.dump(prefs, f, indent=2)


def _get_user_theme(username: str) -> str:
    return _load_theme_prefs().get(username, None)


# ── MAIN TOGGLE ──

def render_theme_toggle(st) -> str:
    """
    Renders a theme toggle in the sidebar.
    - Light mode uses Streamlit's default appearance (no aggressive CSS override)
    - Dark mode uses custom dark CSS
    - Remembers preference per user across sessions (if logged in)
    - Smooth animated transition between themes
    Returns the current theme: 'light' or 'dark'.
    """

    username = st.session_state.get("username", None)

    # ── Step 1: Inject system detection JS ──
    st.markdown(SYSTEM_DETECTION_JS, unsafe_allow_html=True)

    # ── Step 2: Determine initial theme ──
    if "theme" not in st.session_state:
        if username:
            saved = _get_user_theme(username)
            st.session_state["theme"] = saved if saved else "light"
        else:
            st.session_state["theme"] = "light"

    # ── Step 3: Render toggle in sidebar ──
    with st.sidebar:
        st.markdown("---")
        current = st.session_state["theme"]

        badge = "☀️ Light Mode" if current == "light" else "🌙 Dark Mode"
        label = "🌙 Switch to Dark Mode" if current == "light" else "☀️ Switch to Light Mode"

        st.markdown(f'<div class="theme-badge">{badge}</div>', unsafe_allow_html=True)

        if st.button(label, use_container_width=True, key="theme_toggle_btn"):
            new_theme = "dark" if current == "light" else "light"
            st.session_state["theme"] = new_theme

            if username:
                _save_theme_pref(username, new_theme)

            st.rerun()

        if not username:
            st.caption("💡 Log in to save your theme preference.")

    # ── Step 4: Apply CSS ──
    theme = st.session_state["theme"]
    if theme == "dark":
        st.markdown(DARK_THEME, unsafe_allow_html=True)
    else:
        # Light mode — just apply minimal CSS, let Streamlit handle the rest
        st.markdown(LIGHT_RESET, unsafe_allow_html=True)

    return theme
