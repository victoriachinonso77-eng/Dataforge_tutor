# agents/theme_toggle.py — Dark/Light Mode Toggle
# Add to the top of your app.py sidebar to let users switch themes.
# Usage: from agents.theme_toggle import render_theme_toggle
#         render_theme_toggle(st)

import streamlit as st

LIGHT_THEME = """
    <style>
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


def render_theme_toggle(st) -> str:
    """
    Renders a theme toggle in the sidebar.
    Returns the current theme: 'light' or 'dark'.
    Call this at the top of your app.py before rendering any tabs.
    """
    if "theme" not in st.session_state:
        st.session_state["theme"] = "light"

    with st.sidebar:
        st.markdown("---")
        current = st.session_state["theme"]
        label = "🌙 Switch to Dark Mode" if current == "light" else "☀️ Switch to Light Mode"
        badge = "☀️ Light Mode" if current == "light" else "🌙 Dark Mode"

        st.markdown(f'<div class="theme-badge">{badge}</div>', unsafe_allow_html=True)
        if st.button(label, use_container_width=True, key="theme_toggle_btn"):
            st.session_state["theme"] = "dark" if current == "light" else "light"
            st.rerun()

    # Inject the CSS for the current theme
    theme = st.session_state["theme"]
    st.markdown(DARK_THEME if theme == "dark" else LIGHT_THEME, unsafe_allow_html=True)
    return theme
