"""
progress_tab.py — User progress dashboard.
Shows all past quiz sessions, scores over time, mastered vs weak concepts.

Usage in app.py:
    from progress_tab import render_progress_tab
    with tab8:
        render_progress_tab()
"""

import streamlit as st
from auth import get_user_progress


def render_progress_tab():
    st.header("📈 My Progress")
    st.markdown("Track your data science learning journey across all quiz sessions.")

    username = st.session_state.get("current_user", {}).get("username")
    if not username:
        st.warning("Please log in to view your progress.")
        return

    data = get_user_progress(username)
    sessions = data["sessions"]
    stats = data["stats"]

    if not sessions:
        st.info("You haven't completed any Challenge Me sessions yet. Head to the 🧠 Challenge Me tab to get started!")
        return

    # ── Top stats row ──────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Sessions Completed", stats["total_sessions"])
    col2.metric("Average Score", f"{stats['average_score']}%")
    col3.metric("Best Score", f"{stats['best_score']}%")

    improvement = stats["improvement"]
    delta_str = f"+{improvement}%" if improvement > 0 else f"{improvement}%"
    col4.metric("Improvement", delta_str, delta=delta_str)

    st.divider()

    # ── Score over time chart ──────────────────────────────────────────────
    st.subheader("📊 Score Over Time")

    chart_data = {
        "Session": [f"#{i+1}" for i in range(len(sessions))],
        "Score (%)": [s["percentage"] for s in sessions],
    }

    import pandas as pd
    df_chart = pd.DataFrame(chart_data).set_index("Session")
    st.line_chart(df_chart)

    st.divider()

    # ── Concepts ──────────────────────────────────────────────────────────
    col_m, col_w = st.columns(2)

    with col_m:
        st.subheader("✅ Strongest Concepts")
        if stats["top_mastered"]:
            for concept in stats["top_mastered"]:
                st.success(concept.title())
        else:
            st.info("No mastered concepts yet.")

    with col_w:
        st.subheader("📚 Needs More Work")
        if stats["top_weak"]:
            for concept in stats["top_weak"]:
                st.warning(concept.title())
        else:
            st.info("No weak areas identified yet.")

    st.divider()

    # ── Session history ────────────────────────────────────────────────────
    st.subheader("🗂 Session History")

    for i, session in enumerate(reversed(sessions)):
        idx = len(sessions) - i
        pct = session["percentage"]
        badge = session.get("badge", "")
        difficulty = session.get("difficulty", "").title()
        timestamp = session.get("timestamp", "")[:10]  # just the date

        with st.expander(f"Session #{idx} — {pct}% · {badge} · {difficulty} · {timestamp}"):
            col1, col2 = st.columns(2)
            col1.metric("Score", f"{session['score']}/{session['max_score']}")
            col2.metric("Difficulty", difficulty)

            if session.get("mastered_concepts"):
                st.markdown("**Mastered:** " + ", ".join(session["mastered_concepts"]))
            if session.get("weak_concepts"):
                st.markdown("**Weak areas:** " + ", ".join(session["weak_concepts"]))
            if session.get("summary"):
                st.info(session["summary"])