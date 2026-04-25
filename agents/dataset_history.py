# agents/dataset_history.py — Upgraded Dataset History Agent

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

MAX_HISTORY = 10
HISTORY_FILE = "data/dataset_history.json"


# ── PERSISTENCE HELPERS ──

def _load_all_history() -> dict:
    if not os.path.exists(HISTORY_FILE):
        return {}
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_all_history(data: dict) -> None:
    os.makedirs("data", exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _get_user_history(username: str) -> list:
    return _load_all_history().get(username, [])


def _set_user_history(username: str, history: list) -> None:
    all_history = _load_all_history()
    all_history[username] = history
    _save_all_history(all_history)


# ── SAVE TO HISTORY ──

def save_to_history(st, df: pd.DataFrame, filename: str) -> None:
    """
    Call this immediately after a user uploads a dataset.
    Saves to both session state and disk (if logged in).
    """
    username = st.session_state.get("username", None)

    entry = {
        "filename": filename,
        "rows": df.shape[0],
        "cols": df.shape[1],
        "columns": df.columns.tolist()[:10],
        "timestamp": datetime.now().strftime("%d %b %Y, %H:%M"),
        "preview": df.head(3).to_dict(orient="records"),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing": int(df.isnull().sum().sum()),
    }

    # ── Save to session state ──
    if "dataset_history" not in st.session_state:
        st.session_state["dataset_history"] = []

    history = st.session_state["dataset_history"]
    if not history or history[0]["filename"] != filename:
        st.session_state["dataset_history"] = ([entry] + history)[:MAX_HISTORY]

    # ── Save to disk if logged in ──
    if username:
        disk_history = _get_user_history(username)
        if not disk_history or disk_history[0]["filename"] != filename:
            _set_user_history(username, ([entry] + disk_history)[:MAX_HISTORY])


# ── AI SUMMARY ──

def _generate_ai_summary(entry: dict) -> str:
    try:
        import anthropic
        client = anthropic.Anthropic()

        prompt = (
            f"A student uploaded a dataset called '{entry['filename']}' with "
            f"{entry['rows']} rows and {entry['cols']} columns. "
            f"The columns are: {', '.join(entry['columns'])}. "
            f"There are {entry['missing']} missing values total. "
            f"Write a 3-sentence plain English summary of what this dataset is likely about, "
            f"what a student could learn from it, and one thing to watch out for. "
            f"Be friendly and beginner-friendly. No markdown, just plain text."
        )

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception:
        return "AI summary unavailable. Check your API key is configured."


# ── MAIN PANEL ──

def render_history_panel(st) -> None:
    """
    Renders the full dataset history panel.
    Uses disk history if logged in, otherwise falls back to session state.
    """
    st.header("🗂️ Dataset History")
    st.markdown("Your previously uploaded datasets — pick up where you left off.")

    username = st.session_state.get("username", None)

    # Load history — disk if logged in, session if not
    if username:
        history = _get_user_history(username)
        st.caption(f"Showing history for **{username}** — saved across sessions.")
    else:
        history = st.session_state.get("dataset_history", [])
        st.info("💡 Log in to save your dataset history across sessions.")

    if not history:
        st.warning("No dataset history yet. Upload a dataset to get started.")
        return

    # ── SEARCH ──
    search = st.text_input("🔍 Search your history...", placeholder="e.g. titanic, sales, diabetes")

    filtered = history
    if search.strip():
        filtered = [e for e in history if search.strip().lower() in e["filename"].lower()]

    if not filtered:
        st.warning(f"No datasets found matching '{search}'.")
        return

    st.markdown(f"**{len(filtered)} dataset(s) found**")

    # ── CLEAR HISTORY ──
    if username:
        if st.button("🗑️ Clear All History", type="secondary"):
            _set_user_history(username, [])
            st.session_state["dataset_history"] = []
            st.success("History cleared.")
            st.rerun()

    st.markdown("---")

    # ── DISPLAY ENTRIES ──
    for i, entry in enumerate(filtered):
        with st.expander(f"📁 **{entry['filename']}** — {entry['timestamp']}"):

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Rows", f"{entry['rows']:,}")
            with col2:
                st.metric("Columns", entry['cols'])
            with col3:
                st.metric("Missing Values", entry.get('missing', 'N/A'))

            st.markdown("**Columns:**")
            st.markdown(", ".join(f"`{c}`" for c in entry["columns"]))

            # ── PREVIEW ──
            if entry.get("preview"):
                st.markdown("**Preview (first 3 rows):**")
                try:
                    st.dataframe(pd.DataFrame(entry["preview"]), use_container_width=True)
                except Exception:
                    st.caption("Preview unavailable.")

            st.markdown("---")

            col_a, col_b = st.columns(2)

            # ── RELOAD BUTTON ──
            with col_a:
                if st.button("🔄 Reload Dataset", key=f"reload_{i}", use_container_width=True):
                    try:
                        st.session_state["uploaded_df"] = pd.DataFrame(entry["preview"])
                        st.session_state["uploaded_filename"] = entry["filename"]
                        st.success(f"'{entry['filename']}' reloaded! Go to the Upload tab.")
                    except Exception:
                        st.warning("Could not reload this dataset. Please upload it again.")

            # ── AI SUMMARY BUTTON ──
            with col_b:
                if st.button("🤖 AI Summary", key=f"summary_{i}", use_container_width=True):
                    with st.spinner("Generating summary..."):
                        summary = _generate_ai_summary(entry)
                    st.info(summary)
