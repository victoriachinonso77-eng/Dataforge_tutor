"""
Streamlit UI — Tab 7: Challenge Me (Socratic Mode)
Drop this tab into your existing app.py.

Usage in app.py:
    from challenge_tab import render_challenge_tab
    with tab7:
        render_challenge_tab(st.session_state.get("analysis_result"), 
                             st.session_state.get("df"))
"""

import streamlit as st
from agents.socratic import (
    generate_questions,
    evaluate_answer,
    compute_session_result,
    Question,
    AnswerFeedback,
    SessionResult,
)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _analysis_to_summary(analysis_result, df) -> dict:
    """
    Convert whatever your analyser agent returns into the flat dict
    the Socratic agent needs. Adapt field names to match your analyser output.
    """
    import pandas as pd

    summary = {}

    if df is not None:
        summary["shape"] = {"rows": int(df.shape[0]), "columns": int(df.shape[1])}
        summary["columns"] = list(df.columns)
        summary["dtypes"] = {col: str(dtype) for col, dtype in df.dtypes.items()}
        summary["missing_values"] = df.isnull().sum()[df.isnull().sum() > 0].to_dict()
        summary["missing_pct"] = {
            col: round(df[col].isnull().mean() * 100, 2)
            for col in df.columns
            if df[col].isnull().any()
        }

        numeric_cols = df.select_dtypes(include="number")
        if not numeric_cols.empty:
            desc = numeric_cols.describe().round(3)
            summary["numeric_stats"] = desc.to_dict()

            # Skewness
            summary["skewness"] = numeric_cols.skew().round(3).to_dict()

            # Top correlations (flatten to top 5 pairs)
            corr = numeric_cols.corr()
            pairs = []
            seen = set()
            for c1 in corr.columns:
                for c2 in corr.columns:
                    if c1 != c2 and (c2, c1) not in seen:
                        pairs.append((c1, c2, round(float(corr.loc[c1, c2]), 3)))
                        seen.add((c1, c2))
            pairs.sort(key=lambda x: abs(x[2]), reverse=True)
            summary["top_correlations"] = [
                {"col_a": a, "col_b": b, "r": r} for a, b, r in pairs[:5]
            ]

        cat_cols = df.select_dtypes(include="object")
        if not cat_cols.empty:
            summary["categorical_cardinality"] = {
                col: int(df[col].nunique()) for col in cat_cols.columns
            }

    # If your analyser agent returns extra structured data, merge it in
    if analysis_result and isinstance(analysis_result, dict):
        for key in ("insights", "anomalies", "recommendations"):
            if key in analysis_result:
                summary[key] = analysis_result[key]

    return summary


def _score_bar(score: int, max_score: int = 10):
    """Render a small coloured progress bar for a question score."""
    pct = score / max_score
    color = "#22c55e" if pct >= 0.7 else "#f59e0b" if pct >= 0.4 else "#ef4444"
    st.markdown(
        f"""
        <div style="background:#e5e7eb;border-radius:8px;height:10px;margin:4px 0 12px 0">
          <div style="width:{pct*100:.0f}%;background:{color};height:10px;border-radius:8px"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─── Main render function ─────────────────────────────────────────────────────

def render_challenge_tab(analysis_result=None, df=None):
    st.header("🧠 Challenge Me — Socratic Mode")
    st.markdown(
        "_Stop reading. Start thinking._ "
        "The AI will quiz you on **your own dataset** and score your data science reasoning."
    )

    # ── Guard: need a dataset ──────────────────────────────────────────────
    if df is None:
        st.info("📂 Upload and analyse a dataset first (Steps 1–2), then come back here.")
        return

    # ── Session state initialisation ───────────────────────────────────────
    for key, default in [
        ("sq_questions", None),
        ("sq_answers", {}),
        ("sq_feedbacks", {}),
        ("sq_current_idx", 0),
        ("sq_phase", "setup"),      # setup | quiz | results
        ("sq_difficulty", "intermediate"),
        ("sq_summary", None),
        ("sq_analysis_summary", None),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    # ─────────────────────────────────────────────────────────────────────
    # PHASE 1 — SETUP
    # ─────────────────────────────────────────────────────────────────────
    if st.session_state.sq_phase == "setup":
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("Configure your challenge")
            difficulty = st.selectbox(
                "Difficulty level",
                ["beginner", "intermediate", "advanced"],
                index=1,
                help=(
                    "**Beginner** — observation questions\n"
                    "**Intermediate** — interpretation & reasoning\n"
                    "**Advanced** — application & design decisions"
                ),
            )
            n_questions = st.slider("Number of questions", 3, 10, 5)

        with col2:
            st.subheader("Your dataset")
            st.metric("Rows", df.shape[0])
            st.metric("Columns", df.shape[1])
            st.metric("Missing cells", int(df.isnull().sum().sum()))

        st.divider()

        if st.button("🚀 Start Challenge", type="primary", use_container_width=True):
            with st.spinner("Generating your personalised questions…"):
                summary = _analysis_to_summary(analysis_result, df)
                questions = generate_questions(summary, difficulty, n_questions)

            st.session_state.sq_questions = questions
            st.session_state.sq_answers = {}
            st.session_state.sq_feedbacks = {}
            st.session_state.sq_current_idx = 0
            st.session_state.sq_phase = "quiz"
            st.session_state.sq_difficulty = difficulty
            st.session_state.sq_analysis_summary = summary
            st.rerun()

    # ─────────────────────────────────────────────────────────────────────
    # PHASE 2 — QUIZ
    # ─────────────────────────────────────────────────────────────────────
    elif st.session_state.sq_phase == "quiz":
        questions: list[Question] = st.session_state.sq_questions
        idx: int = st.session_state.sq_current_idx
        total = len(questions)

        # Progress bar
        st.progress((idx) / total, text=f"Question {idx + 1} of {total}")

        q = questions[idx]

        # Question card
        st.markdown(
            f"""
            <div style="background:#1e293b;border-left:4px solid #6366f1;
                        padding:16px 20px;border-radius:8px;margin-bottom:16px">
              <p style="color:#a5b4fc;font-size:12px;margin:0 0 6px 0">
                #{q.id} · {q.concept.upper()} · {q.difficulty}
              </p>
              <p style="color:#f1f5f9;font-size:18px;font-weight:600;margin:0">
                {q.text}
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # If already answered — show answer + feedback
        if idx in st.session_state.sq_feedbacks:
            fb: AnswerFeedback = st.session_state.sq_feedbacks[idx]
            user_ans = st.session_state.sq_answers[idx]

            st.markdown(f"**Your answer:** {user_ans}")
            _score_bar(fb.score)

            result_color = "#22c55e" if fb.is_correct else "#ef4444"
            result_icon = "✅" if fb.is_correct else "❌"
            st.markdown(
                f"""
                <div style="background:#0f172a;border:1px solid {result_color};
                            padding:14px;border-radius:8px;margin-bottom:12px">
                  <p style="color:{result_color};font-weight:700;margin:0 0 6px 0">
                    {result_icon} Score: {fb.score}/10
                  </p>
                  <p style="color:#cbd5e1;margin:0">{fb.explanation}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if fb.follow_up:
                st.info(f"💭 **Think further:** {fb.follow_up}")

            col_prev, col_next = st.columns(2)
            with col_prev:
                if idx > 0 and st.button("← Previous"):
                    st.session_state.sq_current_idx -= 1
                    st.rerun()
            with col_next:
                if idx < total - 1:
                    if st.button("Next →", type="primary"):
                        st.session_state.sq_current_idx += 1
                        st.rerun()
                else:
                    if st.button("🏁 See Results", type="primary"):
                        with st.spinner("Calculating your Data Science Readiness Score…"):
                            result = compute_session_result(
                                list(st.session_state.sq_feedbacks.values()),
                                st.session_state.sq_analysis_summary,
                                st.session_state.sq_difficulty,
                            )
                        st.session_state.sq_summary = result
                        st.session_state.sq_phase = "results"
                        st.rerun()

        # Not yet answered — show input
        else:
            with st.expander("💡 Need a hint?"):
                st.markdown(q.hint)

            user_answer = st.text_area(
                "Your answer",
                placeholder="Type your reasoning here… be as detailed as you like.",
                height=130,
                key=f"answer_input_{idx}",
            )

            if st.button("Submit Answer", type="primary", use_container_width=True):
                if not user_answer.strip():
                    st.warning("Please write an answer before submitting.")
                else:
                    running_score = sum(
                        f.score for f in st.session_state.sq_feedbacks.values()
                    )
                    with st.spinner("Evaluating your answer…"):
                        fb = evaluate_answer(
                            q,
                            user_answer,
                            st.session_state.sq_analysis_summary,
                            running_score,
                        )
                    st.session_state.sq_answers[idx] = user_answer
                    st.session_state.sq_feedbacks[idx] = fb
                    st.rerun()

    # ─────────────────────────────────────────────────────────────────────
    # PHASE 3 — RESULTS
    # ─────────────────────────────────────────────────────────────────────
    elif st.session_state.sq_phase == "results":
        result: SessionResult = st.session_state.sq_summary

        st.balloons()
        st.subheader(f"Your Result: {result.badge}")

        # Score ring (CSS hack)
        pct = result.percentage
        ring_color = "#22c55e" if pct >= 70 else "#f59e0b" if pct >= 50 else "#ef4444"
        st.markdown(
            f"""
            <div style="display:flex;justify-content:center;margin:20px 0">
              <div style="position:relative;width:140px;height:140px">
                <svg viewBox="0 0 36 36" style="width:140px;height:140px;transform:rotate(-90deg)">
                  <circle cx="18" cy="18" r="15.9" fill="none"
                          stroke="#1e293b" stroke-width="3.8"/>
                  <circle cx="18" cy="18" r="15.9" fill="none"
                          stroke="{ring_color}" stroke-width="3.8"
                          stroke-dasharray="{pct:.0f} {100-pct:.0f}"
                          stroke-linecap="round"/>
                </svg>
                <div style="position:absolute;top:50%;left:50%;
                            transform:translate(-50%,-50%);text-align:center">
                  <span style="font-size:28px;font-weight:800;color:{ring_color}">{pct:.0f}%</span>
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Score", f"{result.total_score}/{result.max_score}")
        col2.metric("Mastered Concepts", len(result.mastered_concepts))
        col3.metric("Needs Work", len(result.weak_concepts))

        st.divider()
        st.markdown("### 📝 Tutor's Feedback")
        st.markdown(result.summary)

        if result.mastered_concepts:
            st.success(f"✅ Strong on: {', '.join(result.mastered_concepts)}")
        if result.weak_concepts:
            st.warning(f"📚 Review needed: {', '.join(result.weak_concepts)}")

        st.divider()
        st.markdown("### Question-by-Question Breakdown")
        for i, (q, fb) in enumerate(
            zip(
                st.session_state.sq_questions,
                st.session_state.sq_feedbacks.values(),
            )
        ):
            with st.expander(f"Q{i+1}: {q.concept.title()} — {fb.score}/10"):
                st.markdown(f"**Question:** {q.text}")
                st.markdown(f"**Your answer:** {st.session_state.sq_answers[i]}")
                _score_bar(fb.score)
                st.markdown(f"**Feedback:** {fb.explanation}")

        st.divider()
        col_retry, col_harder, col_reset = st.columns(3)

        with col_retry:
            if st.button("🔄 Retry Same Level"):
                st.session_state.sq_phase = "setup"
                st.rerun()

        with col_harder:
            difficulties = ["beginner", "intermediate", "advanced"]
            current = st.session_state.sq_difficulty
            current_idx = difficulties.index(current)
            if current_idx < 2:
                next_diff = difficulties[current_idx + 1]
                if st.button(f"⬆️ Try {next_diff.title()}"):
                    with st.spinner("Generating harder questions…"):
                        questions = generate_questions(
                            st.session_state.sq_analysis_summary,
                            next_diff,
                            len(st.session_state.sq_questions),
                        )
                    st.session_state.sq_questions = questions
                    st.session_state.sq_answers = {}
                    st.session_state.sq_feedbacks = {}
                    st.session_state.sq_current_idx = 0
                    st.session_state.sq_difficulty = next_diff
                    st.session_state.sq_phase = "quiz"
                    st.rerun()

        with col_reset:
            if st.button("📂 New Dataset"):
                for key in [
                    "sq_questions", "sq_answers", "sq_feedbacks",
                    "sq_current_idx", "sq_phase", "sq_summary", "sq_analysis_summary"
                ]:
                    st.session_state[key] = None if "questions" in key or "summary" in key else {}
                st.session_state.sq_phase = "setup"
                st.session_state.sq_current_idx = 0
                st.rerun()
