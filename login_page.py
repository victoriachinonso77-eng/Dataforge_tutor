# login_page.py
# Login and Register UI — shown before app loads
# Blocks app via st.stop() until authenticated

import streamlit as st
from auth import register_user, login_user


def render_login_page():
    if st.session_state.get("authenticated"):
        return True

    st.markdown("""
    <style>
        .stApp { background-color:#0D1117; color:#F0F6FC; }
        section[data-testid="stSidebar"] { display:none; }
        .stButton>button {
            background-color:#02C39A; color:#0D1117;
            font-weight:700; border:none; border-radius:8px;
            width:100%; padding:.6rem;
        }
        .stButton>button:hover { background-color:#028090; color:white; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<br><br>', unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;margin-bottom:1.5rem;">
        <div style="font-size:3rem;font-weight:900;color:#02C39A;">🎓 DataForge</div>
        <div style="color:#8B949E;font-size:1rem;">AI Data Science Tutor</div>
    </div>
    """, unsafe_allow_html=True)

    tab_login, tab_register = st.tabs(["🔑 Login", "📝 Register"])

    with tab_login:
        st.markdown("#### Welcome back")
        username = st.text_input("Username", placeholder="your username",
                                  key="login_username")
        password = st.text_input("Password", type="password",
                                  placeholder="your password",
                                  key="login_password")
        if st.button("Login →", key="login_btn"):
            if not username or not password:
                st.error("Please enter both username and password.")
            else:
                result = login_user(username, password)
                if result["success"]:
                    st.session_state["authenticated"] = True
                    st.session_state["username"]      = result["username"]
                    st.success(f"Welcome back, {result['username']}!")
                    st.rerun()
                else:
                    st.error(result["error"])

    with tab_register:
        st.markdown("#### Create your account")
        new_username = st.text_input("Choose a username",
                                      placeholder="at least 3 characters",
                                      key="reg_username")
        new_password = st.text_input("Choose a password", type="password",
                                      placeholder="at least 6 characters",
                                      key="reg_password")
        confirm_pw   = st.text_input("Confirm password", type="password",
                                      placeholder="repeat your password",
                                      key="reg_confirm")
        if st.button("Create Account →", key="register_btn"):
            if not new_username or not new_password or not confirm_pw:
                st.error("Please fill in all fields.")
            elif new_password != confirm_pw:
                st.error("Passwords do not match.")
            else:
                result = register_user(new_username, new_password)
                if result["success"]:
                    st.success("Account created! You can now log in.")
                else:
                    st.error(result["error"])

    st.stop()
    return False


def render_logout_button():
    col1, col2 = st.columns([5, 1])
    with col2:
        if st.button("Logout", key="logout_btn"):
            for key in ["authenticated", "username"]:
                st.session_state.pop(key, None)
            st.rerun()
    return col1