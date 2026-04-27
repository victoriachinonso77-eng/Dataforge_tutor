# agents/multi_dataset_tab.py — Upgraded Multi Dataset Comparison Tab

import streamlit as st
import pandas as pd


def generate_ai_insight(client, df1, df1_name, df2, df2_name):
    """Uses GPT-4 to generate a plain English comparison of two datasets."""
    if not client:
        return "Add your OpenAI API key to enable AI insights."
    try:
        shared_cols = list(set(df1.columns) & set(df2.columns))
        prompt = f"""You are a data science tutor. A student has uploaded two datasets and wants to understand the differences.

Dataset 1: '{df1_name}'
- Shape: {df1.shape[0]} rows x {df1.shape[1]} columns
- Columns: {list(df1.columns)[:10]}
- Missing values: {int(df1.isnull().sum().sum())}
- Duplicates: {int(df1.duplicated().sum())}

Dataset 2: '{df2_name}'
- Shape: {df2.shape[0]} rows x {df2.shape[1]} columns
- Columns: {list(df2.columns)[:10]}
- Missing values: {int(df2.isnull().sum().sum())}
- Duplicates: {int(df2.duplicated().sum())}

Shared columns: {shared_cols[:5] if shared_cols else 'None'}

Write a 4-5 sentence plain English explanation of:
1. What each dataset likely contains
2. The key structural differences
3. Which dataset appears cleaner and why
4. What a student should investigate next

Be friendly, educational, and beginner-friendly. No markdown, just plain text."""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"AI insight unavailable: {e}"


def render_multi_dataset_tab(gpt_client=None):
    st.markdown("### 📊 Multi Dataset Comparison")
    st.markdown("Upload two datasets and compare them side by side — structure, quality, and statistics.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**📂 Dataset 1**")
        file1 = st.file_uploader("Upload first dataset", type=["csv"], key="ds1")

    with col2:
        st.markdown("**📂 Dataset 2**")
        file2 = st.file_uploader("Upload second dataset", type=["csv"], key="ds2")

    if not file1 or not file2:
        st.info("👆 Upload two CSV datasets above to start comparing.")
        return

    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    st.divider()

    # ── OVERVIEW METRICS ──
    st.markdown("### 📋 Overview")
    col_a, col_b, col_c, col_d = st.columns(4)

    with col_a:
        st.metric("Dataset 1 Rows", f"{df1.shape[0]:,}")
        st.metric("Dataset 2 Rows", f"{df2.shape[0]:,}")
    with col_b:
        st.metric("Dataset 1 Columns", df1.shape[1])
        st.metric("Dataset 2 Columns", df2.shape[1])
    with col_c:
        st.metric("Dataset 1 Missing", int(df1.isnull().sum().sum()))
        st.metric("Dataset 2 Missing", int(df2.isnull().sum().sum()))
    with col_d:
        st.metric("Dataset 1 Duplicates", int(df1.duplicated().sum()))
        st.metric("Dataset 2 Duplicates", int(df2.duplicated().sum()))

    st.divider()

    # ── MISSING VALUES PERCENTAGE ──
    st.markdown("### 🔍 Missing Values (%)")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**{file1.name}**")
        missing1 = (df1.isnull().sum() / len(df1) * 100).round(1)
        missing1 = missing1[missing1 > 0]
        if not missing1.empty:
            for col, pct in missing1.items():
                st.markdown(f"- `{col}`: {pct}% missing")
        else:
            st.success("No missing values!")

    with col2:
        st.markdown(f"**{file2.name}**")
        missing2 = (df2.isnull().sum() / len(df2) * 100).round(1)
        missing2 = missing2[missing2 > 0]
        if not missing2.empty:
            for col, pct in missing2.items():
                st.markdown(f"- `{col}`: {pct}% missing")
        else:
            st.success("No missing values!")

    st.divider()

    # ── DATA TYPES COMPARISON ──
    st.markdown("### 🗂️ Column and Data Type Comparison")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**{file1.name}**")
        dtypes1 = pd.DataFrame({
            "Column": df1.columns,
            "Type": df1.dtypes.astype(str).values
        })
        st.dataframe(dtypes1, use_container_width=True, hide_index=True)

    with col2:
        st.markdown(f"**{file2.name}**")
        dtypes2 = pd.DataFrame({
            "Column": df2.columns,
            "Type": df2.dtypes.astype(str).values
        })
        st.dataframe(dtypes2, use_container_width=True, hide_index=True)

    # ── SHARED COLUMNS ──
    shared = set(df1.columns) & set(df2.columns)
    only_in_1 = set(df1.columns) - set(df2.columns)
    only_in_2 = set(df2.columns) - set(df1.columns)

    st.divider()
    st.markdown("### 🔗 Column Overlap")

    c1, c2, c3 = st.columns(3)
    with c1:
        if shared:
            st.success(f"**Shared ({len(shared)}):**")
            for col in shared:
                st.markdown(f"- `{col}`")
        else:
            st.warning("No shared columns")
    with c2:
        if only_in_1:
            st.info(f"**Only in {file1.name} ({len(only_in_1)}):**")
            for col in only_in_1:
                st.markdown(f"- `{col}`")
    with c3:
        if only_in_2:
            st.info(f"**Only in {file2.name} ({len(only_in_2)}):**")
            for col in only_in_2:
                st.markdown(f"- `{col}`")

    # ── COLUMN MATCH SCORE ──
    total_cols = len(set(df1.columns) | set(df2.columns))
    match_score = round(len(shared) / total_cols * 100) if total_cols > 0 else 0
    similarity = "High similarity" if match_score > 70 else "Low similarity" if match_score < 30 else "Moderate similarity"
    st.markdown(f"**Column Match Score: {match_score}%** — {similarity}")

    st.divider()

    # ── STATISTICAL SUMMARY FOR SHARED COLUMNS ──
    numeric_shared = [c for c in shared if
                      pd.api.types.is_numeric_dtype(df1[c]) and
                      pd.api.types.is_numeric_dtype(df2[c])]

    if numeric_shared:
        st.markdown("### 📈 Statistical Summary (Shared Numeric Columns)")
        for col in numeric_shared[:5]:
            st.markdown(f"**`{col}`**")
            stat_col1, stat_col2 = st.columns(2)
            with stat_col1:
                st.markdown(f"*{file1.name}*")
                stats1 = df1[col].describe().round(2)
                st.dataframe(stats1.to_frame(), use_container_width=True)
            with stat_col2:
                st.markdown(f"*{file2.name}*")
                stats2 = df2[col].describe().round(2)
                st.dataframe(stats2.to_frame(), use_container_width=True)

        st.divider()

    # ── AI INSIGHT ──
    st.markdown("### 🤖 AI Insight")
    st.markdown("Get a plain English explanation of the key differences between your two datasets.")

    if st.button("Generate AI Insight", use_container_width=True):
        with st.spinner("GPT-4 is analysing your datasets..."):
            insight = generate_ai_insight(
                gpt_client, df1, file1.name, df2, file2.name
            )
        st.markdown(
            f'<div style="background:#161B22;border-left:4px solid #02C39A;'
            f'padding:1rem 1.4rem;border-radius:0 8px 8px 0;color:#E6EDF3;'
            f'font-size:.95rem;line-height:1.6">'
            f'🤖 {insight}</div>',
            unsafe_allow_html=True)
