# agents/dataset_history.py
import streamlit as st
import json
import os
from datetime import datetime

HISTORY_FILE = "data/dataset_history.json"


def _load_history():
    os.makedirs("data", exist_ok=True)
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE) as f:
            return json.load(f)
    return {}


def _save_history(history):
    os.makedirs("data", exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2, default=str)


def save_dataset_session(username, dataset_name, shape,
                          key_findings, ai_summary=""):
    history = _load_history()
    if username not in history:
        history[username] = {"sessions": []}
    history[username]["sessions"].append({
        "dataset":      dataset_name,
        "rows":         shape[0],
        "cols":         shape[1],
        "key_findings": key_findings[:5],
        "ai_summary":   ai_summary,
        "timestamp":    datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    _save_history(history)


def get_user_history(username):
    history = _load_history()
    return history.get(username, {}).get("sessions", [])


def generate_dataset_summary(client, df, insights, audit_log):
    if not client:
        return _template_summary(df, insights, audit_log)
    import pandas as pd
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    correlations = insights.get("strong_correlations", [])
    skewed       = insights.get("skewed_columns", {})
    corr_text = (", ".join(f"{p['col_a']}↔{p['col_b']}(r={p['correlation']})"
                           for p in correlations[:2])
                 if correlations else "no strong correlations")
    prompt = f"""Summarise this dataset in 3 sentences for a student.
Dataset: {df.shape[0]} rows x {df.shape[1]} columns
Numeric columns: {numeric_cols[:6]}
Correlations: {corr_text}
Cleaning steps: {len(audit_log)} transformations
Skewed: {list(skewed.keys())[:3] if skewed else 'none'}
Write: (1) what dataset contains, (2) most interesting finding, (3) what to explore next."""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200, temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Summary error: {e}")
        return _template_summary(df, insights, audit_log)


def _template_summary(df, insights, audit_log):
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    correlations = insights.get("strong_correlations", [])
    finding = ""
    if correlations:
        p = correlations[0]
        finding = (f"The most notable finding is a "
                   f"{'positive' if p['correlation']>0 else 'negative'} "
                   f"correlation (r={p['correlation']}) between "
                   f"{p['col_a']} and {p['col_b']}.")
    else:
        finding = "No strong correlations were found between numeric columns."
    return (f"This dataset contains {df.shape[0]:,} rows and {df.shape[1]} columns "
            f"with {len(numeric_cols)} numeric features. "
            f"{finding} "
            f"DataForge applied {len(audit_log)} cleaning transformations.")


def render_conversation_history():
    chat_history = st.session_state.get("chat_history", [])
    if not chat_history:
        st.info("No conversation history yet. Ask the tutor a question in the "
                "💬 Ask the Tutor tab.")
        return
    st.markdown(f"**{len(chat_history) // 2} interaction(s) this session**")
    st.divider()
    interactions = []
    for i in range(0, len(chat_history) - 1, 2):
        if (chat_history[i]["role"] == "user" and
                chat_history[i+1]["role"] == "tutor"):
            interactions.append((chat_history[i], chat_history[i+1]))
    for idx, (user_msg, tutor_msg) in enumerate(interactions):
        with st.expander(
            f"Q{idx+1}: {user_msg['text'][:60]}"
            f"{'...' if len(user_msg['text'])>60 else ''}",
            expanded=(idx == len(interactions)-1)
        ):
            st.markdown(
                f'<div style="background:#1C2333;border-radius:10px;'
                f'padding:.8rem 1rem;margin-bottom:.5rem;color:#E6EDF3">'
                f'🧑‍🎓 {user_msg["text"]}</div>',
                unsafe_allow_html=True)
            st.markdown(
                f'<div style="background:#161B22;border:1px solid #028090;'
                f'border-radius:10px;padding:.8rem 1rem;color:#E6EDF3">'
                f'🎓 {tutor_msg["text"]}</div>',
                unsafe_allow_html=True)
            if tutor_msg.get("code"):
                with st.expander("📋 Code snippet"):
                    st.code(tutor_msg["code"], language="python")
            bookmark_key = f"bookmark_{idx}"
            bookmarks = st.session_state.get("bookmarks", [])
            is_bookmarked = idx in bookmarks
            if st.button(
                "🔖 Bookmarked" if is_bookmarked else "🔖 Bookmark this",
                key=bookmark_key
            ):
                if is_bookmarked:
                    bookmarks.remove(idx)
                else:
                    bookmarks.append(idx)
                st.session_state["bookmarks"] = bookmarks
                st.rerun()
    bookmarks = st.session_state.get("bookmarks", [])
    if bookmarks:
        st.divider()
        st.markdown("#### 🔖 Your Bookmarks")
        for idx in bookmarks:
            if idx < len(interactions):
                user_msg, tutor_msg = interactions[idx]
                st.markdown(f"**Q{idx+1}:** {user_msg['text'][:80]}...")
                st.markdown(
                    f'<div style="background:#0D2137;border-left:3px solid #02C39A;'
                    f'padding:.6rem 1rem;border-radius:0 6px 6px 0;'
                    f'font-size:.9rem;color:#E6EDF3">'
                    f'{tutor_msg["text"][:200]}...</div>',
                    unsafe_allow_html=True)


def render_dataset_history(username):
    sessions = get_user_history(username)
    if not sessions:
        st.info("No datasets analysed yet. Upload a dataset and run the "
                "pipeline to start building your history.")
        return
    st.markdown(f"**{len(sessions)} dataset(s) analysed**")
    st.divider()
    for i, session in enumerate(reversed(sessions)):
        with st.expander(
            f"📂 {session['dataset']} — {session['timestamp']} | "
            f"{session['rows']:,} rows × {session['cols']} cols",
            expanded=(i == 0)
        ):
            if session.get("ai_summary"):
                st.markdown(
                    f'<div style="background:#161B22;border-left:4px solid #02C39A;'
                    f'padding:.8rem 1rem;border-radius:0 8px 8px 0;color:#E6EDF3">'
                    f'🤖 {session["ai_summary"]}</div>',
                    unsafe_allow_html=True)
            if session.get("key_findings"):
                st.markdown("**Key findings:**")
                for finding in session["key_findings"]:
                    st.markdown(f"- {finding}")
