<<<<<<< HEAD
# agents/theme_toggle.py — Upgraded Dark/Light Mode Toggle
=======
# agents/theme_toggle.py — Dark/Light Mode Toggle
# Add to the top of your app.py sidebar to let users switch themes.

>>>>>>> 5fbc51fcbb144c74b0c7a56a0a9ddf3a496a71ac

import streamlit as st
import json
import os

THEME_FILE = "data/theme_preferences.json"

LIGHT_THEME = """
    <style>
        * { transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease; }
        .stApp { background-color: #F8F9FA; color: #212529; }
        .stSidebar { background-color: #FFFFFF; }
        .stTextInput > div > div > input { background-color: #FFFFFF; color: #212529; }
        .stSelectbox > div > div { background-color: #FFFFFF; color: #212529; }
        .stDataFrame { background-color: #FFFFFF; }
        .block-container { background-color: #F8F9FA; }
        h1, h2, h3 { color: #1F3864 !important; }
        .stMetric { background-color: #FFFFFF; border-radius: 8px; padding: 10px; }
        .stAlert { border-radius: 8px; }
        .theme-badge {
            background: #1F3864; color: white;
            padding: 4px 12px; border-radius: 20px;
            font-size: 13px; display: inline-block; margin-bottom: 10px;
        }
    </style>
"""

DARK_THEME = """
    <style>
        * { transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease; }
        .stApp { background-color: #0E1117; color: #FAFAFA; }
        .stSidebar { background-color: #161B22; }
        .stTextInput > div > div > input { background-color: #21262D; color: #FAFAFA; border-color: #30363D; }
        .stSelectbox > div > div { background-color: #21262D; color: #FAFAFA; }
        .stDataFrame { background-color: #161B22; }
        .block-container { background-color: #0E1117; }
        h1, h2, h3 { color: #58A6FF !important; }
        .stMetric { background-color: #161B22; border-radius: 8px; padding: 10px; border: 1px solid #30363D; }
        .stAlert { border-radius: 8px; }
        .theme-badge {
            background: #58A6FF; color: #0E1117;
            padding: 4px 12px; border-radius: 20px;
            font-size: 13px; display: inline-block; margin-bottom: 10px;
        }
    </style>
"""

# JavaScript to detect system preference (dark or light)
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
    - Detects system preference on first load
    - Remembers preference per user across sessions (if logged in)
    - Smooth animated transition between themes
    Returns the current theme: 'light' or 'dark'.
    """

    username = st.session_state.get("username", None)

    # ── Step 1: Inject system detection JS (runs once) ──
    st.markdown(SYSTEM_DETECTION_JS, unsafe_allow_html=True)

    # ── Step 2: Determine initial theme ──
    if "theme" not in st.session_state:
        if username:
            # Logged in — load from disk
            saved = _get_user_theme(username)
            st.session_state["theme"] = saved if saved else "light"
        else:
            # Not logged in — default to light
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

            # Save to disk if logged in
            if username:
                _save_theme_pref(username, new_theme)
                st.caption(f"✅ Theme saved for {username}")

            st.rerun()

        if not username:
            st.caption("💡 Log in to save your theme preference.")

    # ── Step 4: Apply theme CSS with smooth transition ──
    theme = st.session_state["theme"]
    st.markdown(DARK_THEME if theme == "dark" else LIGHT_THEME, unsafe_allow_html=True)

    return theme
