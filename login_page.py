# login_page.py
import streamlit as st
from auth import register_user, login_user

MASCOT_LOGIN = """
<svg width="90" height="90" viewBox="0 0 72 72" fill="none" xmlns="http://www.w3.org/2000/svg">
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


def render_login_page():
    if st.session_state.get("authenticated"):
        return True

    st.markdown("""
    <style>
        .stApp { background-color:#0D1117; color:#F0F6FC; }
        section[data-testid="stSidebar"] { display:none; }

        .login-wrapper {
            max-width: 420px;
            margin: 2rem auto;
            padding: 0 1rem;
        }
        .login-mascot {
            text-align: center;
            margin-bottom: 1.2rem;
        }
        .login-title {
            font-size: 2rem;
            font-weight: 900;
            color: #02C39A;
            text-align: center;
            margin: 0;
            line-height: 1.2;
        }
        .login-sub {
            font-size: 0.88rem;
            color: #8B949E;
            text-align: center;
            margin: 4px 0 1.5rem;
        }
        .login-card {
            background: #111827;
            border: 1px solid #1E293B;
            border-radius: 16px;
            padding: 1.8rem 1.6rem;
        }
        .login-divider {
            height: 1px;
            background: #1E293B;
            margin: 1rem 0;
        }
        .login-features {
            display: flex;
            justify-content: center;
            gap: 1.5rem;
            margin-top: 1.5rem;
            flex-wrap: wrap;
        }
        .login-feature {
            text-align: center;
            font-size: 0.78rem;
            color: #8B949E;
        }
        .login-feature-icon {
            font-size: 1.3rem;
            display: block;
            margin-bottom: 3px;
        }
        .stButton>button {
            background-color: #02C39A !important;
            color: #0D1117 !important;
            font-weight: 700 !important;
            border: none !important;
            border-radius: 10px !important;
            width: 100%;
            padding: 0.55rem !important;
            font-size: 0.95rem !important;
            transition: all 0.2s !important;
        }
        .stButton>button:hover {
            background-color: #028090 !important;
            color: white !important;
            transform: translateY(-1px) !important;
        }
        .stTabs [data-baseweb="tab"] {
            color: #8B949E;
            font-size: 0.9rem;
        }
        .stTabs [aria-selected="true"] {
            color: #02C39A !important;
            border-bottom-color: #02C39A !important;
            font-weight: 600;
        }
        input {
            background: #0D1117 !important;
            color: #F0F6FC !important;
            border-radius: 10px !important;
            border-color: #1E293B !important;
        }
        #MainMenu{visibility:hidden} footer{visibility:hidden}
    </style>
    """, unsafe_allow_html=True)

    # Mascot and title
    st.markdown(
        f'<div class="login-mascot">{MASCOT_LOGIN}</div>'
        f'<p class="login-title">DataForge</p>'
        f'<p class="login-sub">Your AI Data Science Tutor</p>',
        unsafe_allow_html=True)

    # Login / Register tabs inside a card
    st.markdown('<div class="login-card">', unsafe_allow_html=True)

    tab_login, tab_register = st.tabs(["🔑  Login", "📝  Register"])

    with tab_login:
        st.markdown("##### Welcome back")
        username = st.text_input("Username", placeholder="your username",
                                  key="login_username")
        password = st.text_input("Password", type="password",
                                  placeholder="your password",
                                  key="login_password")
        st.markdown("")
        if st.button("Login →", key="login_btn"):
            if not username or not password:
                st.error("Please enter both username and password.")
            else:
                result = login_user(username, password)
                if result["success"]:
                    st.session_state["authenticated"] = True
                    st.session_state["username"]      = result["username"]
                    st.success(f"Welcome back, {result['username']}! 👋")
                    st.rerun()
                else:
                    st.error(result["error"])

    with tab_register:
        st.markdown("##### Create your account")
        new_username = st.text_input("Choose a username",
                                      placeholder="at least 3 characters",
                                      key="reg_username")
        new_password = st.text_input("Choose a password", type="password",
                                      placeholder="at least 6 characters",
                                      key="reg_password")
        confirm_pw   = st.text_input("Confirm password", type="password",
                                      placeholder="repeat your password",
                                      key="reg_confirm")
        st.markdown("")
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

    st.markdown('</div>', unsafe_allow_html=True)

    # Feature highlights below card
    st.markdown("""
    <div class="login-features">
        <div class="login-feature">
            <span class="login-feature-icon">🤖</span>
            12 AI Agents
        </div>
        <div class="login-feature">
            <span class="login-feature-icon">🎓</span>
            Personalised lessons
        </div>
        <div class="login-feature">
            <span class="login-feature-icon">🔊</span>
            Voice narration
        </div>
        <div class="login-feature">
            <span class="login-feature-icon">🏆</span>
            Earn certificates
        </div>
        <div class="login-feature">
            <span class="login-feature-icon">🧠</span>
            Socratic quizzes
        </div>
    </div>
    """, unsafe_allow_html=True)

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