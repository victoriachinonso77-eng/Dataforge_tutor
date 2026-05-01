# challenge_tab.py
# Socratic Challenge Mode UI
# Called from app.py inside the Challenge Me tab

import streamlit as st
from agents.socratic import (generate_questions, grade_answer,
                              get_badge, get_session_summary,
                              DIFFICULTY_LABELS, BADGES)
from auth import save_session


def render_challenge_tab(cleaned_df, insights, audit_log,
                          gpt_client, level, username):
    """
    Renders the full Socratic Challenge Me tab.
    Requires a cleaned dataset, insights dict, and audit log from the pipeline.
    """
    st.markdown("### 🧠 Socratic Challenge Mode")
    st.markdown(
        "DataForge will quiz you on your actual dataset findings. "
        "Answers are graded 0–10 with a strict rubric — you must reference "
        "specific details from your data to score above 4."
    )

    # ── Difficulty selector ────────────────────────────────────────────
    st.divider()
    col_d1, col_d2, col_d3 = st.columns([2, 2, 3])
    with col_d1:
        difficulty = st.selectbox(
            "Difficulty level",
            options=["beginner", "intermediate", "advanced"],
            index=["beginner", "intermediate", "advanced"].index(
                st.session_state.get("challenge_difficulty", level)),
            key="challenge_difficulty_select",
            format_func=lambda x: DIFFICULTY_LABELS[x]
        )
        st.session_state["challenge_difficulty"] = difficulty
    with col_d2:
        n_questions = st.selectbox("Number of questions", [3, 5, 7, 10],
                                    index=1, key="challenge_n_q")
    with col_d3:
        st.markdown("")
        st.markdown("")
        if st.button("🚀 Start Challenge", key="start_challenge",
                     use_container_width=True):
            st.session_state["challenge_active"]   = True
            st.session_state["challenge_questions"] = None
            st.session_state["challenge_answers"]   = {}
            st.session_state["challenge_scores"]    = {}
            st.session_state["challenge_followups"] = {}
            st.session_state["challenge_complete"]  = False
            st.rerun()

    # ── Not started yet ────────────────────────────────────────────────
    if not st.session_state.get("challenge_active"):
        st.info(
            "👆 Choose your difficulty level and click **Start Challenge** to begin. "
            "Questions are generated from your actual dataset findings."
        )
        _show_badge_guide()
        return

    # ── Generate questions if not yet done ────────────────────────────
    if st.session_state.get("challenge_questions") is None:
        with st.spinner("GPT-4 is generating questions from your dataset..."):
            questions = generate_questions(
                client     = gpt_client,
                df         = cleaned_df,
                insights   = insights,
                audit_log  = audit_log,
                difficulty = difficulty,
                n_questions = n_questions,
            )
        st.session_state["challenge_questions"] = questions

    questions = st.session_state["challenge_questions"]
    answers   = st.session_state.get("challenge_answers", {})
    scores    = st.session_state.get("challenge_scores", {})
    followups = st.session_state.get("challenge_followups", {})
    complete  = st.session_state.get("challenge_complete", False)

    # ── Render each question ───────────────────────────────────────────
    if not complete:
        st.markdown(f"**{len(questions)} questions — {DIFFICULTY_LABELS[difficulty]} level**")
        st.markdown(
            "> 💡 Reference specific numbers, column names, and findings "
            "from your dataset to score 5 or above."
        )
        st.divider()

        for qi, q in enumerate(questions):
            already_answered = str(qi) in scores

            with st.expander(
                f"Q{qi+1}: {q['question'][:80]}{'...' if len(q['question'])>80 else ''}",
                expanded=not already_answered
            ):
                st.markdown(f"**{q['question']}**")
                st.caption(f"Concept: {q['concept']} · Difficulty: {DIFFICULTY_LABELS[q.get('difficulty', difficulty)]}")

                if already_answered:
                    # Show graded result
                    score_data = scores[str(qi)]
                    _render_score(score_data)
                    if str(qi) in followups:
                        st.markdown(
                            f'<div style="background:#0D2137;border-left:3px solid #028090;'
                            f'padding:.7rem 1rem;border-radius:0 6px 6px 0;margin-top:.5rem">'
                            f'💭 <strong>Follow-up:</strong> {followups[str(qi)]}'
                            f'</div>', unsafe_allow_html=True)
                else:
                    # Answer input
                    answer_key = f"challenge_ans_{qi}"
                    user_answer = st.text_area(
                        "Your answer",
                        placeholder="Write your answer here — reference specific "
                                    "columns, numbers, or findings from your dataset...",
                        key=answer_key,
                        height=120,
                        label_visibility="collapsed"
                    )
                    if st.button(f"Submit Answer", key=f"submit_q_{qi}"):
                        if not user_answer or not user_answer.strip():
                            st.warning("Please write an answer before submitting.")
                        else:
                            with st.spinner("GPT-4 is grading your answer..."):
                                grade = grade_answer(
                                    client         = gpt_client,
                                    question       = q["question"],
                                    student_answer = user_answer,
                                    ideal_points   = q.get("ideal_answer_points", []),
                                    concept        = q.get("concept", "data science"),
                                    difficulty     = difficulty,
                                )
                            st.session_state["challenge_answers"][str(qi)] = user_answer
                            st.session_state["challenge_scores"][str(qi)]  = grade
                            st.session_state["challenge_followups"][str(qi)] = grade.get("follow_up", "")
                            st.rerun()

        # ── Submit all button ──────────────────────────────────────────
        answered_count = len(scores)
        st.divider()
        progress_pct = answered_count / len(questions)
        st.progress(progress_pct,
                    text=f"{answered_count}/{len(questions)} questions answered")

        if answered_count == len(questions):
            if st.button("🏁 See My Results", key="finish_challenge",
                         use_container_width=True):
                st.session_state["challenge_complete"] = True
                st.rerun()
        elif answered_count > 0:
            st.info(f"Answer all {len(questions)} questions to see your results and badge.")

    # ── Results screen ─────────────────────────────────────────────────
    else:
        _render_results(questions, scores, followups, difficulty,
                        gpt_client, username, cleaned_df)


def _render_score(score_data: dict):
    """Renders a coloured score pill and feedback."""
    score     = score_data.get("score", 0)
    max_score = score_data.get("max_score", 10)
    label     = score_data.get("grade_label", "Graded")
    feedback  = score_data.get("feedback", "")

    colour = ("#166534" if score >= 8 else
              "#1D4ED8" if score >= 5 else
              "#92400E" if score >= 3 else "#7F1D1D")
    text_colour = "#86EFAC" if score >= 8 else "#BFDBFE" if score >= 5 else "#FCD34D" if score >= 3 else "#FCA5A5"

    st.markdown(
        f'<div style="background:{colour};border-radius:8px;padding:.5rem 1rem;'
        f'display:inline-block;margin-bottom:.5rem">'
        f'<span style="color:{text_colour};font-weight:bold">'
        f'{score}/{max_score} — {label}</span></div>',
        unsafe_allow_html=True
    )
    if feedback:
        st.markdown(
            f'<div style="background:#1C2333;border-radius:6px;padding:.7rem 1rem;'
            f'color:#C9D1D9;font-size:.9rem">{feedback}</div>',
            unsafe_allow_html=True
        )


def _render_results(questions, scores, followups, difficulty,
                    gpt_client, username, cleaned_df):
    """Renders the final results screen with badge and session save."""
    score_list = [scores[str(i)] for i in range(len(questions))
                  if str(i) in scores]
    total     = sum(s["score"] for s in score_list)
    max_total = len(questions) * 10
    badge     = get_badge(total, max_total)

    # Badge display
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0D2137,#1E3A5F);
                border:2px solid {badge.get('color','#028090')};
                border-radius:14px;padding:2rem;text-align:center;margin:1rem 0">
        <div style="font-size:3.5rem">{badge.get('emoji','🏆')}</div>
        <div style="font-size:1.8rem;font-weight:900;color:{badge.get('color','#028090')}">
            {badge.get('name','Completed')}
        </div>
        <div style="color:#E6EDF3;font-size:1.1rem;margin:.5rem 0">
            {total}/{max_total} points ({badge.get('pct',0):.0f}%)
        </div>
        <div style="color:#8B949E;font-size:.9rem">
            {DIFFICULTY_LABELS.get(difficulty, difficulty)} level · 
            {len(questions)} questions
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Score breakdown
    st.markdown("### 📋 Question-by-Question Breakdown")
    for qi, q in enumerate(questions):
        if str(qi) in scores:
            score_data = scores[str(qi)]
            s          = score_data.get("score", 0)
            icon       = "🟢" if s >= 8 else "🔵" if s >= 5 else "🟡" if s >= 3 else "🔴"
            with st.expander(f"{icon} Q{qi+1}: {q['question'][:60]}... — {s}/10"):
                st.markdown(f"**Concept:** {q.get('concept','')}")
                _render_score(score_data)

    # Save session to progress tracker
    session_data = {
        "score":        total,
        "max_score":    max_total,
        "difficulty":   difficulty,
        "n_questions":  len(questions),
        "badge":        badge.get("name", ""),
        "pct":          badge.get("pct", 0),
        "dataset_cols": list(cleaned_df.columns)[:8],
        "questions":    [{"q": q["question"], "concept": q["concept"],
                          "score": scores.get(str(i), {}).get("score", 0)}
                         for i, q in enumerate(questions)],
    }
    if username:
        save_session(username, session_data)

    # Retry / upgrade buttons
    st.divider()
    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1:
        if st.button("🔄 Try Again (same level)", use_container_width=True):
            st.session_state["challenge_active"]    = True
            st.session_state["challenge_questions"] = None
            st.session_state["challenge_answers"]   = {}
            st.session_state["challenge_scores"]    = {}
            st.session_state["challenge_followups"] = {}
            st.session_state["challenge_complete"]  = False
            st.rerun()
    with col_r2:
        next_levels = {"beginner": "intermediate", "intermediate": "advanced"}
        next_level  = next_levels.get(difficulty)
        if next_level and st.button(
                f"⬆️ Upgrade to {DIFFICULTY_LABELS[next_level]}",
                use_container_width=True):
            st.session_state["challenge_difficulty"] = next_level
            st.session_state["challenge_active"]     = True
            st.session_state["challenge_questions"]  = None
            st.session_state["challenge_answers"]    = {}
            st.session_state["challenge_scores"]     = {}
            st.session_state["challenge_followups"]  = {}
            st.session_state["challenge_complete"]   = False
            st.rerun()
    with col_r3:
        if st.button("📊 View My Progress", use_container_width=True):
            st.info("Switch to the 📈 My Progress tab to see your full history.")


def _show_badge_guide():
    """Shows the badge earning guide."""
    st.markdown("#### 🏆 Badges You Can Earn")
    cols = st.columns(4)
    badge_list = [
        ("🌱", "Novice", "0%+", "#6B7280"),
        ("📊", "Analyst", "40%+", "#3B82F6"),
        ("🔬", "Data Scientist", "65%+", "#8B5CF6"),
        ("🏆", "Expert", "85%+", "#F59E0B"),
    ]
    for col, (emoji, name, threshold, color) in zip(cols, badge_list):
        col.markdown(
            f'<div style="background:#161B22;border:1px solid {color};'
            f'border-radius:8px;padding:.8rem;text-align:center">'
            f'<div style="font-size:1.8rem">{emoji}</div>'
            f'<div style="font-weight:bold;color:{color}">{name}</div>'
            f'<div style="font-size:.8rem;color:#8B949E">{threshold}</div>'
            f'</div>', unsafe_allow_html=True
        )