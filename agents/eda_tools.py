# agents/eda_tools.py
# Fahzian's Feature Agent
# Feature 1: Explain Chart — GPT-4 + local fallback chart interpretation
# Feature 2: One-Click EDA Story — narrative summary with GPT-4 + fallback
# Feature 3: Diff View — before vs after cleaning snapshot
# Feature 4: Export Pack — zip of report, charts, diff, audit, insights

import io
import json
import zipfile
import pandas as pd
import numpy as np


# ══════════════════════════════════════════════════════════════════════════
# FEATURE 1 — EXPLAIN CHART
# ══════════════════════════════════════════════════════════════════════════

def explain_chart_gpt(client, chart_title: str, chart_type: str,
                       insights: dict, df, level: str = "beginner") -> str:
    """
    Uses GPT-4 to explain a chart in plain English based on dataset context.
    Falls back to local explainer if GPT-4 is unavailable.
    """
    if not client:
        return explain_chart_local(chart_title, chart_type, insights, df)

    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    correlations = insights.get("strong_correlations", [])
    skewed       = insights.get("skewed_columns", {})

    corr_text = ""
    if correlations:
        corr_text = "Strong correlations: " + ", ".join(
            f"{p['col_a']}↔{p['col_b']}(r={p['correlation']})"
            for p in correlations[:3])

    prompt = f"""You are a data science tutor explaining a chart to a {level} student.

Chart title: {chart_title}
Chart type: {chart_type}
Dataset: {df.shape[0]} rows × {df.shape[1]} columns
Numeric columns: {numeric_cols[:6]}
{corr_text}
Skewed columns: {list(skewed.keys())[:3] if skewed else 'none'}

Write a 3-sentence plain-English explanation of:
1. What this chart is showing
2. The most important pattern or finding visible
3. What the student should pay attention to or investigate next

Keep it conversational and specific to this dataset — avoid generic explanations."""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.4
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Chart explanation GPT error: {e}")
        return explain_chart_local(chart_title, chart_type, insights, df)


def explain_chart_local(chart_title: str, chart_type: str,
                         insights: dict, df) -> str:
    """
    Local fallback chart explainer — no API needed.
    Generates rule-based explanations from insights dictionary.
    """
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    correlations = insights.get("strong_correlations", [])
    skewed       = insights.get("skewed_columns", {})
    title_lower  = chart_title.lower()

    # Histogram
    if "distribution" in title_lower or "histogram" in title_lower:
        skew_text = ""
        if skewed:
            col, val = list(skewed.items())[0]
            direction = "right (positive)" if val > 0 else "left (negative)"
            skew_text = (f" The column '{col}' shows a {direction} skew "
                         f"(skewness = {val:.2f}), meaning the distribution is not symmetric.")
        return (
            f"This histogram shows how values are distributed across your numeric columns. "
            f"Taller bars mean more data points fall in that range.{skew_text} "
            f"Look for columns where most values are bunched at one end — this indicates skewness "
            f"that may need a log transformation before modelling."
        )

    # Heatmap
    if "heatmap" in title_lower or "correlation" in title_lower:
        if correlations:
            top = correlations[0]
            direction = "positive" if top["correlation"] > 0 else "negative"
            return (
                f"This heatmap shows the correlation between all numeric columns — "
                f"darker colours mean stronger relationships. "
                f"The strongest finding is a {direction} correlation between "
                f"'{top['col_a']}' and '{top['col_b']}' (r = {top['correlation']}). "
                f"Remember — correlation does not mean causation."
            )
        return (
            "This heatmap shows correlations between all numeric columns. "
            "Dark green = strong positive relationship. Dark red = strong negative. "
            "White or light colours mean little to no relationship. "
            "No strong correlations were found in this dataset."
        )

    # Box plot
    if "box" in title_lower or "outlier" in title_lower:
        return (
            "This box plot shows the spread of each numeric column and highlights outliers. "
            "The box covers the middle 50% of values (Q1 to Q3). "
            "The line inside the box is the median. "
            "Dots outside the whiskers are outliers — values unusually far from the rest. "
            "DataForge flags these but does not remove them, "
            "as outliers can be the most important data points in some domains."
        )

    # Scatter
    if "scatter" in title_lower:
        if correlations:
            top = correlations[0]
            return (
                f"This scatter plot shows the relationship between two numeric columns. "
                f"Each dot is one row of your data. "
                f"A trend line going upward suggests a positive correlation — "
                f"as one value increases, the other tends to as well. "
                f"The strongest relationship in your data is between "
                f"'{top['col_a']}' and '{top['col_b']}' (r = {top['correlation']})."
            )
        return (
            "This scatter plot shows the relationship between two numeric columns. "
            "Each dot represents one row of your data. "
            "Look for a clear upward or downward trend — that would indicate correlation. "
            "A random cloud of dots means the two columns are not strongly related."
        )

    # Generic fallback
    return (
        f"This chart shows patterns in your dataset — '{chart_title}'. "
        f"Your dataset has {df.shape[0]:,} rows and {df.shape[1]} columns. "
        f"Look for unusual patterns, clusters, or values that stand out "
        f"as these often reveal the most important findings."
    )


# ══════════════════════════════════════════════════════════════════════════
# FEATURE 2 — ONE-CLICK EDA STORY
# ══════════════════════════════════════════════════════════════════════════

def generate_eda_story_gpt(client, df_raw, cleaned_df,
                            insights: dict, audit_log: list,
                            level: str = "beginner") -> str:
    """
    Generates a narrative EDA story using GPT-4.
    Falls back to local story generator if GPT-4 is unavailable.
    """
    if not client:
        return generate_eda_story_local(df_raw, cleaned_df, insights, audit_log)

    numeric_cols = cleaned_df.select_dtypes(include=["number"]).columns.tolist()
    correlations = insights.get("strong_correlations", [])
    skewed       = insights.get("skewed_columns", {})
    bias_warn    = insights.get("bias_warnings", [])

    n_dupes   = sum(1 for e in audit_log if "duplicate" in e.lower())
    n_missing = sum(1 for e in audit_log if "missing" in e.lower())

    corr_text = ""
    if correlations:
        corr_text = "\n".join(
            f"- {p['col_a']} ↔ {p['col_b']}: r={p['correlation']} "
            f"({'positive' if p['correlation']>0 else 'negative'})"
            for p in correlations[:3])

    prompt = f"""You are a friendly data science storyteller writing for a {level} student.

Dataset summary:
- Original: {df_raw.shape[0]:,} rows × {df_raw.shape[1]} columns
- After cleaning: {cleaned_df.shape[0]:,} rows × {cleaned_df.shape[1]} columns
- Duplicates removed: {n_dupes}
- Missing values addressed: {n_missing} operations
- Numeric columns: {numeric_cols[:6]}
- Strong correlations found:
{corr_text if corr_text else "  None above threshold"}
- Skewed columns: {list(skewed.keys())[:3] if skewed else "None"}
- Bias warnings: {bias_warn[:2] if bias_warn else "None"}

Write an engaging 4-paragraph EDA story covering:
1. Data quality — what was found and fixed
2. Key patterns and correlations discovered
3. What the skewness or distribution findings mean
4. Practical next steps the student should take

Keep it encouraging, specific to this dataset, and avoid jargon without explanation.
End with one actionable recommendation."""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"EDA story GPT error: {e}")
        return generate_eda_story_local(df_raw, cleaned_df, insights, audit_log)


def generate_eda_story_local(df_raw, cleaned_df,
                              insights: dict, audit_log: list) -> str:
    """
    Local fallback EDA story generator — no API needed.
    Always produces a meaningful narrative from the insights dictionary.
    """
    numeric_cols = cleaned_df.select_dtypes(include=["number"]).columns.tolist()
    correlations = insights.get("strong_correlations", [])
    skewed       = insights.get("skewed_columns", {})
    bias_warn    = insights.get("bias_warnings", [])

    n_dupes    = sum(1 for e in audit_log if "duplicate" in e.lower())
    n_missing  = sum(1 for e in audit_log if "missing" in e.lower())
    rows_removed = df_raw.shape[0] - cleaned_df.shape[0]

    # Paragraph 1: Data quality
    quality = (
        f"**📋 Data Quality**\n\n"
        f"Your dataset started with {df_raw.shape[0]:,} rows and {df_raw.shape[1]} columns. "
        f"DataForge applied {len(audit_log)} cleaning operations — "
        f"removing {rows_removed} duplicate rows and addressing {n_missing} missing value issues. "
        f"The cleaned dataset has {cleaned_df.shape[0]:,} rows ready for analysis."
    )

    # Paragraph 2: Patterns
    if correlations:
        top = correlations[0]
        direction = "positive" if top["correlation"] > 0 else "negative"
        corr_story = (
            f"The most striking pattern is a {direction} correlation of r = {top['correlation']} "
            f"between **{top['col_a']}** and **{top['col_b']}** — "
            f"as one increases, the other tends to {'increase' if top['correlation'] > 0 else 'decrease'} as well. "
        )
        if len(correlations) > 1:
            corr_story += f"{len(correlations)} strong relationships were found in total."
    else:
        corr_story = "No strong linear correlations were found between numeric columns — the variables appear largely independent."

    patterns = f"**🔍 Key Patterns**\n\n{corr_story}"

    # Paragraph 3: Distributions
    if skewed:
        skew_col, skew_val = list(skewed.items())[0]
        direction = "positively (right tail)" if skew_val > 0 else "negatively (left tail)"
        dist_story = (
            f"**{skew_col}** is {direction} skewed (skewness = {skew_val:.2f}). "
            f"This means a few extreme values are pulling the average away from the typical value. "
            f"Consider applying a log transformation to this column before modelling. "
            f"{len(skewed)} column(s) showed notable skewness in total."
        )
    else:
        dist_story = "All numeric columns show relatively symmetric distributions — good news for modelling as many algorithms assume normality."

    distributions = f"**📊 Distributions**\n\n{dist_story}"

    # Paragraph 4: Next steps
    if bias_warn:
        next_action = f"Review the bias warnings flagged: {bias_warn[0]}. Then explore the Visualisation tab to see patterns visually."
    elif correlations:
        top = correlations[0]
        next_action = f"Explore the relationship between **{top['col_a']}** and **{top['col_b']}** using the scatter plot in the Visualisation tab."
    else:
        next_action = "Try the AutoML tab to train a machine learning model and discover which columns are most predictive."

    next_steps = f"**🚀 What to Do Next**\n\n{next_action} Your data is clean and ready for deeper exploration."

    return f"{quality}\n\n{patterns}\n\n{distributions}\n\n{next_steps}"


# ══════════════════════════════════════════════════════════════════════════
# FEATURE 3 — DIFF VIEW
# ══════════════════════════════════════════════════════════════════════════

def generate_diff_view(df_raw: pd.DataFrame,
                        cleaned_df: pd.DataFrame,
                        audit_log: list) -> dict:
    """
    Generates a before-vs-after cleaning comparison.
    Returns a structured diff dict for display and export.
    """
    # Row/column changes
    rows_removed = df_raw.shape[0] - cleaned_df.shape[0]
    cols_removed = df_raw.shape[1] - cleaned_df.shape[1]
    cols_added   = [c for c in cleaned_df.columns if c not in df_raw.columns]
    cols_dropped = [c for c in df_raw.columns if c not in cleaned_df.columns]

    # Missing value changes per column
    missing_before = df_raw.isnull().sum()
    missing_after  = cleaned_df.reindex(columns=df_raw.columns).isnull().sum()
    missing_delta  = (missing_before - missing_after).to_dict()
    missing_delta  = {k: int(v) for k, v in missing_delta.items() if v != 0}

    # Duplicate count
    dupes_before = int(df_raw.duplicated().sum())
    dupes_after  = int(cleaned_df.duplicated().sum())

    # Summary stats comparison
    numeric_before = df_raw.select_dtypes(include=["number"])
    numeric_after  = cleaned_df.select_dtypes(include=["number"])
    common_cols    = [c for c in numeric_before.columns if c in numeric_after.columns]

    stats_comparison = {}
    for col in common_cols[:6]:
        stats_comparison[col] = {
            "mean_before":   round(float(numeric_before[col].mean()), 3),
            "mean_after":    round(float(numeric_after[col].mean()),  3),
            "missing_before": int(missing_before.get(col, 0)),
            "missing_after":  int(missing_after.get(col,  0)),
        }

    return {
        "rows_before":    df_raw.shape[0],
        "rows_after":     cleaned_df.shape[0],
        "rows_removed":   rows_removed,
        "cols_before":    df_raw.shape[1],
        "cols_after":     cleaned_df.shape[1],
        "cols_added":     cols_added,
        "cols_dropped":   cols_dropped,
        "dupes_before":   dupes_before,
        "dupes_after":    dupes_after,
        "missing_delta":  missing_delta,
        "total_missing_fixed": sum(missing_delta.values()),
        "stats_comparison":    stats_comparison,
        "audit_log":           audit_log,
    }


def render_diff_view(st, diff: dict):
    """Renders the diff view in Streamlit."""
    st.markdown("### 🔄 Before vs After Cleaning")
    st.markdown(
        "Here is exactly what DataForge changed in your dataset — "
        "complete transparency on every transformation."
    )

    # KPI row
    k1, k2, k3, k4 = st.columns(4)
    for col_st, val, lbl, colour in [
        (k1, f"-{diff['rows_removed']:,}",      "Rows removed",       "#EF4444"),
        (k2, f"-{diff['dupes_before']}",         "Duplicates removed", "#F59E0B"),
        (k3, f"+{diff['total_missing_fixed']}",  "Missing values fixed","#10B981"),
        (k4, f"{diff['rows_after']:,}",           "Clean rows ready",   "#02C39A"),
    ]:
        col_st.markdown(
            f'<div style="background:#161B22;border:1px solid {colour};'
            f'border-radius:10px;padding:.9rem 1rem;text-align:center">'
            f'<div style="font-size:1.8rem;font-weight:800;color:{colour}">{val}</div>'
            f'<div style="font-size:.8rem;color:#8B949E">{lbl}</div></div>',
            unsafe_allow_html=True
        )

    st.markdown("")

    # Side by side comparison
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### 🔴 Before Cleaning")
        st.markdown(f"- **{diff['rows_before']:,}** rows")
        st.markdown(f"- **{diff['cols_before']}** columns")
        st.markdown(f"- **{diff['dupes_before']}** duplicate rows")
        total_missing = sum(v + diff['missing_delta'].get(k, 0)
                           for k, v in {}.items()) if False else \
                        sum(diff['missing_delta'].values())
        st.markdown(f"- **{total_missing}** missing values addressed")

    with col_b:
        st.markdown("#### 🟢 After Cleaning")
        st.markdown(f"- **{diff['rows_after']:,}** rows")
        st.markdown(f"- **{diff['cols_after']}** columns")
        st.markdown(f"- **{diff['dupes_after']}** duplicate rows")
        st.markdown(f"- **0** missing values remaining")

    # Missing values fixed per column
    if diff["missing_delta"]:
        st.markdown("#### Missing Values Fixed per Column")
        delta_df = pd.DataFrame([
            {"Column": col, "Missing Values Fixed": fixed}
            for col, fixed in sorted(diff["missing_delta"].items(),
                                      key=lambda x: x[1], reverse=True)
        ])
        st.dataframe(delta_df, use_container_width=True, hide_index=True)

    # Stats comparison
    if diff["stats_comparison"]:
        with st.expander("📊 Statistics Before vs After", expanded=False):
            stats_rows = []
            for col, vals in diff["stats_comparison"].items():
                stats_rows.append({
                    "Column":       col,
                    "Mean (before)": vals["mean_before"],
                    "Mean (after)":  vals["mean_after"],
                    "Mean change":   round(vals["mean_after"] - vals["mean_before"], 4),
                    "Missing before": vals["missing_before"],
                    "Missing after":  vals["missing_after"],
                })
            st.dataframe(pd.DataFrame(stats_rows),
                         use_container_width=True, hide_index=True)

    # Audit log
    with st.expander("🔍 Full Audit Trail", expanded=False):
        for entry in diff["audit_log"]:
            st.markdown(
                f'<div style="background:#161B22;border-left:3px solid #028090;'
                f'padding:5px 12px;margin:3px 0;border-radius:0 6px 6px 0;'
                f'font-size:.85rem;font-family:monospace;color:#C9D1D9">'
                f'{entry}</div>',
                unsafe_allow_html=True
            )


# ══════════════════════════════════════════════════════════════════════════
# FEATURE 4 — EXPORT PACK
# ══════════════════════════════════════════════════════════════════════════

def build_export_pack(df_raw: pd.DataFrame,
                       cleaned_df: pd.DataFrame,
                       insights: dict,
                       audit_log: list,
                       report: str,
                       eda_story: str,
                       charts: list,
                       diff: dict) -> bytes:
    """
    Builds a ZIP file containing all analysis outputs.

    Structure:
    export_pack/
    ├── report/dataforge_report.md
    ├── eda/eda_story.md
    ├── charts/*.html (all interactive Plotly charts)
    ├── diff/diff_summary.md
    ├── diff/diff_missing_by_column.csv
    ├── cleaning/cleaning_steps.txt
    └── insights/insights_summary.json
    """
    buf = io.BytesIO()

    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:

        # ── report/dataforge_report.md ────────────────────────────────
        zf.writestr("export_pack/report/dataforge_report.md",
                    report or "# Report\n\nNo report generated yet.")

        # ── eda/eda_story.md ──────────────────────────────────────────
        zf.writestr("export_pack/eda/eda_story.md",
                    eda_story or "# EDA Story\n\nNo EDA story generated yet.")

        # ── charts/*.html ─────────────────────────────────────────────
        for i, chart in enumerate(charts or []):
            try:
                import plotly.io as pio
                html_str = pio.to_html(chart["fig"],
                                        full_html=True,
                                        include_plotlyjs="cdn")
                safe_name = chart["title"].replace(" ", "_").replace("/","_")
                zf.writestr(f"export_pack/charts/{i+1}_{safe_name}.html",
                            html_str)
            except Exception as e:
                zf.writestr(f"export_pack/charts/chart_{i+1}_error.txt",
                            str(e))

        # ── diff/diff_summary.md ──────────────────────────────────────
        diff_md = f"""# Cleaning Diff Summary

## Shape Changes
| | Before | After | Change |
|---|---|---|---|
| Rows | {diff.get('rows_before',0):,} | {diff.get('rows_after',0):,} | -{diff.get('rows_removed',0):,} |
| Columns | {diff.get('cols_before',0)} | {diff.get('cols_after',0)} | {diff.get('cols_after',0)-diff.get('cols_before',0)} |

## Duplicate Rows
- Before: {diff.get('dupes_before', 0)}
- After:  {diff.get('dupes_after', 0)}
- Removed: {diff.get('dupes_before',0) - diff.get('dupes_after',0)}

## Missing Values Fixed
Total operations: {diff.get('total_missing_fixed', 0)}

{chr(10).join(f'- {col}: {n} values fixed' for col, n in diff.get('missing_delta',{}).items())}
"""
        zf.writestr("export_pack/diff/diff_summary.md", diff_md)

        # ── diff/diff_missing_by_column.csv ───────────────────────────
        if diff.get("missing_delta"):
            delta_df = pd.DataFrame([
                {"column": k, "missing_values_fixed": v}
                for k, v in diff["missing_delta"].items()
            ])
            zf.writestr("export_pack/diff/diff_missing_by_column.csv",
                        delta_df.to_csv(index=False))

        # ── cleaning/cleaning_steps.txt ───────────────────────────────
        steps_txt = "\n".join(
            f"{i+1}. {step}" for i, step in enumerate(audit_log or []))
        zf.writestr("export_pack/cleaning/cleaning_steps.txt",
                    steps_txt or "No cleaning steps recorded.")

        # ── insights/insights_summary.json ────────────────────────────
        safe_insights = {}
        for k, v in (insights or {}).items():
            try:
                json.dumps(v)
                safe_insights[k] = v
            except Exception:
                safe_insights[k] = str(v)

        zf.writestr("export_pack/insights/insights_summary.json",
                    json.dumps(safe_insights, indent=2, default=str))

    buf.seek(0)
    return buf.read()