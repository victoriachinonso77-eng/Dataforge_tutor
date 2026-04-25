"""
login_page.py — Streamlit login and registration UI.
Call render_login_page() before anything else in app.py.
"""

import streamlit as st
from auth import login_user, register_user


def render_login_page():
    """
    Renders the login/register gate.
    Returns True if user is authenticated, False otherwise.
    Call this at the TOP of app.py before rendering any tabs.
    """

    # Already logged in — pass through
    if st.session_state.get("authenticated"):
        return True

    # ── Page styling ──────────────────────────────────────────────────────
    st.markdown("""
        <div style="text-align:center; padding: 40px 0 10px 0">
            <h1 style="font-size:48px">🔬 DataForge</h1>
            <p style="color:#94a3b8; font-size:18px">
                Autonomous Data Science · Powered by AI
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ── Tabs: Login / Register ────────────────────────────────────────────
    login_tab, register_tab = st.tabs(["🔑 Login", "📝 Create Account"])

    # ── LOGIN ─────────────────────────────────────────────────────────────
    with login_tab:
        st.subheader("Welcome back")

        username = st.text_input("Username", key="login_username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")

        if st.button("Login", type="primary", use_container_width=True, key="login_btn"):
            if not username or not password:
                st.warning("Please fill in both fields.")
            else:
                success, message, user_data = login_user(username, password)
                if success:
                    st.session_state["authenticated"] = True
                    st.session_state["current_user"] = user_data
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

    # ── REGISTER ──────────────────────────────────────────────────────────
    with register_tab:
        st.subheader("Create your account")

        new_display = st.text_input("Display Name", key="reg_display", placeholder="e.g. Abdulmalik")
        new_username = st.text_input("Username", key="reg_username", placeholder="Choose a username")
        new_password = st.text_input("Password", type="password", key="reg_password", placeholder="At least 6 characters")
        confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm", placeholder="Repeat your password")

        if st.button("Create Account", type="primary", use_container_width=True, key="register_btn"):
            if not new_username or not new_password or not confirm_password:
                st.warning("Please fill in all fields.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                success, message = register_user(new_username, new_password, new_display)
                if success:
                    st.success(message + " Please log in.")
                else:
                    st.error(message)

    return False


def render_user_header():
    """
    Renders a small header bar showing the logged-in user with a logout button.
    Call this at the TOP of your main app content (after the login gate passes).
    """
    user = st.session_state.get("current_user", {})
    display_name = user.get("display_name", "User")

    col1, col2 = st.columns([8, 1])
    with col1:
        st.markdown(f"👤 Logged in as **{display_name}**")
    with col2:
        if st.button("Logout", key="logout_btn"):
            for key in ["authenticated", "current_user"]:
                st.session_state.pop(key, None)
            st.rerun()