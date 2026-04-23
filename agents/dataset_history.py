# agents/dataset_history.py — Dataset History Agent
# Remembers the last 5 datasets a user uploaded so they can reload them quickly.
# Usage: from agents.dataset_history import save_to_history, render_history_panel
#        Call save_to_history(st, df, filename) whenever a user uploads a dataset.
#        Call render_history_panel(st) in the sidebar or a dedicated section.

import streamlit as st
import pandas as pd
import json
from datetime import datetime

MAX_HISTORY = 5


def save_to_history(st, df: pd.DataFrame, filename: str) -> None:
    """
    Saves a dataset to the session history.
    Stores up to MAX_HISTORY entries. Oldest entry is removed when full.
    Call this immediately after a user uploads or loads a dataset.
    """
    if "dataset_history" not in st.session_state:
        st.session_state["dataset_history"] = []

    # Avoid duplicate consecutive saves of the same file
    history = st.session_state["dataset_history"]
    if history and history[0]["filename"] == filename:
        return

    entry = {
        "filename": filename,
        "rows": df.shape[0],
        "cols": df.shape[1],
        "columns": df.columns.tolist()[:8],  # Store first 8 column names
        "timestamp": datetime.now().strftime("%d %b %Y, %H:%M"),
        "preview": df.head(3).to_dict(orient="records"),
    }

    # Prepend new entry and trim to max
    st.session_state["dataset_history"] = ([entry] + history)[:MAX_HISTORY]


def render_history_panel(st) -> None:
    """
    Renders a dataset history panel.
    Displays the last 5 datasets with a Reload button for each.
    Returns the reloaded DataFrame via st.session_state['uploaded_df'].
    """
    if "dataset_history" not in st.session_state or not st.session_state["dataset_history"]:
        st.info("No dataset history yet. Upload a dataset to get started.")
        return

    history = st.session_state["dataset_history"]
    st.markdown(f"**{len(history)} recent dataset(s):**")

    for i, entry in enumerate(history):
        with st.container():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{entry['filename']}**")
                st.caption(
                    f"📅 {entry['timestamp']}  •  "
                    f"📊 {entry['rows']:,} rows × {entry['cols']} cols  •  "
                    f"Columns: {', '.join(entry['columns'])}"
                    + ("..." if entry['cols'] > 8 else "")
                )
            with col2:
                if st.button("↩ Reload", key=f"reload_hist_{i}", use_container_width=True):
                    # Reconstruct the DataFrame from the stored preview
                    preview_df = pd.DataFrame(entry["preview"])
                    st.session_state["uploaded_df"] = preview_df
                    st.session_state["dataset_name"] = entry["filename"]
                    st.warning(
                        f"⚠️ Reloaded a preview of '{entry['filename']}' "
                        f"(first 3 rows only). Re-upload the file for the full dataset."
                    )
                    st.rerun()
            st.divider()


def render_history_sidebar(st) -> None:
    """
    Compact version for the sidebar — shows filenames only with reload buttons.
    """
    if "dataset_history" not in st.session_state or not st.session_state["dataset_history"]:
        return

    history = st.session_state["dataset_history"]
    st.sidebar.markdown("### 🕓 Recent Datasets")

    for i, entry in enumerate(history):
        col1, col2 = st.sidebar.columns([3, 1])
        with col1:
            st.markdown(f"<small>{entry['filename']}</small>", unsafe_allow_html=True)
            st.caption(f"{entry['rows']:,} rows")
        with col2:
            if st.button("↩", key=f"sidebar_reload_{i}", help=f"Reload {entry['filename']}"):
                preview_df = pd.DataFrame(entry["preview"])
                st.session_state["uploaded_df"] = preview_df
                st.session_state["dataset_name"] = entry["filename"]
                st.rerun()
