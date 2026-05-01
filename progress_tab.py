# progress_tab.py
# My Progress Dashboard — score history, concept mastery, improvement over time

import streamlit as st
import pandas as pd
from auth import get_user_progress


def render_progress_tab(username: str):
    """Renders the full My Progress dashboard for the logged-in user."""
    st.markdown("### 📈 My Progress")
    st.markdown(f"Tracking your learning journey, **{username}**.")

    data     = get_user_progress(username)
    sessions = data.get("sessions", [])

    if not sessions:
        st.info(
            "No sessions recorded yet. Complete a **🧠 Challenge Me** quiz "
            "to start tracking your progress!"
        )
        return

    # ── Key metrics ────────────────────────────────────────────────────
    total_sessions = len(sessions)
    latest_pct     = sessions[-1].get("pct", 0)
    first_pct      = sessions[0].get("pct", 0)
    improvement    = latest_pct - first_pct
    best_pct       = max(s.get("pct", 0) for s in sessions)
    best_badge     = max(sessions, key=lambda s: s.get("pct", 0)).get("badge", "")

    k1, k2, k3, k4 = st.columns(4)
    for col_st, val, lbl in [
        (k1, total_sessions,        "Sessions Completed"),
        (k2, f"{latest_pct:.0f}%",  "Latest Score"),
        (k3, f"{best_pct:.0f}%",    "Personal Best"),
        (k4, f"{improvement:+.0f}%", "Improvement"),
    ]:
        col_st.markdown(
            f'<div style="background:#161B22;border:1px solid #028090;'
            f'border-radius:10px;padding:.9rem 1rem">'
            f'<div style="font-size:1.8rem;font-weight:800;color:#02C39A">{val}</div>'
            f'<div style="font-size:.8rem;color:#8B949E">{lbl}</div></div>',
            unsafe_allow_html=True
        )

    if best_badge:
        st.markdown(f"**🏆 Best badge achieved:** {best_badge}")

    st.divider()

    # ── Score over time chart ──────────────────────────────────────────
    st.markdown("#### Score Over Time")
    score_data = pd.DataFrame([
        {
            "Session":    f"Session {i+1}",
            "Score (%)":  round(s.get("pct", 0), 1),
            "Difficulty": s.get("difficulty", "").title(),
            "Badge":      s.get("badge", ""),
            "Date":       s.get("timestamp", ""),
        }
        for i, s in enumerate(sessions)
    ])

    try:
        import plotly.express as px
        fig = px.line(
            score_data,
            x="Session", y="Score (%)",
            color="Difficulty",
            markers=True,
            title="Quiz Score Progression",
            color_discrete_map={
                "Beginner":     "#02C39A",
                "Intermediate": "#3B82F6",
                "Advanced":     "#8B5CF6",
            }
        )
        fig.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            yaxis=dict(range=[0, 105]),
            xaxis_title="Session", yaxis_title="Score (%)"
        )
        fig.add_hline(y=85, line_dash="dot", line_color="#F59E0B",
                      annotation_text="Expert threshold (85%)")
        fig.add_hline(y=65, line_dash="dot", line_color="#8B5CF6",
                      annotation_text="Data Scientist (65%)")
        st.plotly_chart(fig, use_container_width=True)
    except ImportError:
        st.line_chart(score_data.set_index("Session")["Score (%)"])

    st.divider()

    # ── Concept mastery breakdown ──────────────────────────────────────
    st.markdown("#### Concept Mastery")
    st.markdown("*Based on all quiz sessions — higher is better*")

    concept_scores = {}
    for session in sessions:
        for q in session.get("questions", []):
            concept = q.get("concept", "Unknown")
            score   = q.get("score", 0)
            if concept not in concept_scores:
                concept_scores[concept] = []
            concept_scores[concept].append(score)

    if concept_scores:
        concept_df = pd.DataFrame([
            {
                "Concept":       concept,
                "Avg Score":     round(sum(scores) / len(scores), 1),
                "Times Tested":  len(scores),
                "Mastery":       "✅ Strong" if sum(scores)/len(scores) >= 7
                                 else "🔵 Developing" if sum(scores)/len(scores) >= 4
                                 else "🔴 Needs work"
            }
            for concept, scores in concept_scores.items()
        ]).sort_values("Avg Score", ascending=False)

        st.dataframe(
            concept_df,
            use_container_width=True,
            hide_index=True
        )

        # Strongest and weakest
        strongest = concept_df.iloc[0]["Concept"] if len(concept_df) > 0 else ""
        weakest   = concept_df.iloc[-1]["Concept"] if len(concept_df) > 0 else ""

        col_s, col_w = st.columns(2)
        with col_s:
            st.success(f"💪 Strongest concept: **{strongest}**")
        with col_w:
            st.warning(f"📚 Focus area: **{weakest}**")

    st.divider()

    # ── Full session history ───────────────────────────────────────────
    st.markdown("#### Full Session History")
    for i, session in enumerate(reversed(sessions)):
        pct        = session.get("pct", 0)
        badge      = session.get("badge", "")
        difficulty = session.get("difficulty", "").title()
        n_q        = session.get("n_questions", 0)
        timestamp  = session.get("timestamp", "")
        score      = session.get("score", 0)
        max_score  = session.get("max_score", n_q * 10)

        icon = ("🟢" if pct >= 85 else "🔵" if pct >= 65 else
                "🟡" if pct >= 40 else "🔴")

        with st.expander(
            f"{icon} Session {len(sessions)-i}: {pct:.0f}% — {badge} | "
            f"{difficulty} | {timestamp}",
            expanded=(i == 0)
        ):
            st.markdown(f"**Score:** {score}/{max_score} ({pct:.0f}%)")
            st.markdown(f"**Badge:** {badge}")
            st.markdown(f"**Difficulty:** {difficulty}")
            st.markdown(f"**Questions:** {n_q}")

            qs = session.get("questions", [])
            if qs:
                st.markdown("**Question breakdown:**")
                for q in qs:
                    q_score  = q.get("score", 0)
                    q_icon   = "🟢" if q_score >= 8 else "🔵" if q_score >= 5 else "🔴"
                    st.markdown(
                        f"- {q_icon} **{q.get('concept','')}** — "
                        f"{q_score}/10 — _{q.get('q','')[:60]}..._"
                    )