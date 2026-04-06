# agents/visualiser_plotly.py
# Agent 3 (v2) — Interactive Plotly Visualisations

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# DataForge colour palette
TEAL   = "#02C39A"
TEAL2  = "#028090"
NAVY   = "#0D2137"
GREY   = "#94A3B8"
RED    = "#F87171"
ORANGE = "#F59E0B"
PURPLE = "#8B5CF6"

PALETTE = [TEAL, TEAL2, ORANGE, RED, PURPLE, "#38BDF8", "#34D399", "#FB923C"]

LAYOUT = dict(
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(family="Arial", color="#1E293B"),
    title_font=dict(size=16, color="#0D2137", family="Arial Black"),
    margin=dict(l=40, r=40, t=60, b=40),
    colorway=PALETTE,
)


def generate_plotly_charts(df: pd.DataFrame, insights: dict) -> list[dict]:
    """
    Generates interactive Plotly charts based on data profile.
    Returns list of {"title": str, "fig": plotly.Figure} dicts.
    """
    charts = []
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols     = df.select_dtypes(include=["object", "category"]).columns.tolist()

    # ── 1. Distribution histograms ────────────────────────────────────────
    if numeric_cols:
        cols_to_plot = numeric_cols[:4]
        n = len(cols_to_plot)
        fig = make_subplots(rows=1, cols=n,
                            subplot_titles=[c.replace("_", " ").title() for c in cols_to_plot])
        for i, col in enumerate(cols_to_plot):
            fig.add_trace(go.Histogram(
                x=df[col].dropna(), name=col,
                marker_color=PALETTE[i % len(PALETTE)],
                opacity=0.85, showlegend=False
            ), row=1, col=i+1)
        fig.update_layout(title_text="Numeric Distributions", **LAYOUT)
        charts.append({"title": "Numeric Distributions", "fig": fig})

    # ── 2. Correlation heatmap ────────────────────────────────────────────
    if len(numeric_cols) > 1:
        corr = df[numeric_cols].corr().round(3)
        fig = go.Figure(data=go.Heatmap(
            z=corr.values,
            x=corr.columns.tolist(),
            y=corr.columns.tolist(),
            colorscale=[[0, RED], [0.5, "white"], [1, TEAL]],
            zmid=0,
            text=corr.values.round(2),
            texttemplate="%{text}",
            textfont={"size": 10},
            hoverongaps=False
        ))
        fig.update_layout(title_text="Correlation Heatmap", **LAYOUT)
        charts.append({"title": "Correlation Heatmap", "fig": fig})

    # ── 3. Box plots for outlier detection ───────────────────────────────
    if numeric_cols:
        cols_box = numeric_cols[:4]
        fig = go.Figure()
        for i, col in enumerate(cols_box):
            fig.add_trace(go.Box(
                y=df[col].dropna(), name=col.replace("_", " ").title(),
                marker_color=PALETTE[i % len(PALETTE)],
                boxmean=True
            ))
        fig.update_layout(title_text="Outlier Detection — Box Plots",
                          showlegend=False, **LAYOUT)
        charts.append({"title": "Outlier Detection", "fig": fig})

    # ── 4. Category bar charts ────────────────────────────────────────────
    for col in cat_cols[:2]:
        vc = df[col].value_counts().head(10)
        fig = px.bar(x=vc.index.astype(str), y=vc.values,
                     labels={"x": col.replace("_", " ").title(), "y": "Count"},
                     title=f"Top Values — {col.replace('_', ' ').title()}",
                     color_discrete_sequence=PALETTE)
        fig.update_layout(**LAYOUT)
        fig.update_traces(marker_line_width=0)
        charts.append({"title": f"Category: {col}", "fig": fig})

    # ── 5. Scatter plot for top correlation ───────────────────────────────
    strong = insights.get("strong_correlations", [])
    if strong:
        top = strong[0]
        col_a, col_b = top["col_a"], top["col_b"]
        fig = px.scatter(df, x=col_a, y=col_b,
                         title=f"Scatter: {col_a} vs {col_b}  (r = {top['correlation']})",
                         trendline="ols",
                         color_discrete_sequence=[TEAL],
                         labels={col_a: col_a.replace("_"," ").title(),
                                 col_b: col_b.replace("_"," ").title()})
        fig.update_layout(**LAYOUT)
        fig.update_traces(marker=dict(size=5, opacity=0.6))
        charts.append({"title": f"Scatter (r={top['correlation']})", "fig": fig})

    # ── 6. Missing values bar ─────────────────────────────────────────────
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if not missing.empty:
        fig = px.bar(x=missing.index, y=missing.values,
                     labels={"x": "Column", "y": "Missing Count"},
                     title="Remaining Missing Values",
                     color_discrete_sequence=[RED])
        fig.update_layout(**LAYOUT)
        charts.append({"title": "Missing Values", "fig": fig})

    # ── 7. Skewness bar ───────────────────────────────────────────────────
    skewed = insights.get("skewed_columns", {})
    if skewed:
        cols_sk = list(skewed.keys())
        vals_sk = [skewed[c] for c in cols_sk]
        colors = [RED if abs(v) > 2 else ORANGE for v in vals_sk]
        fig = go.Figure(go.Bar(x=cols_sk, y=vals_sk,
                               marker_color=colors,
                               text=[f"{v:.2f}" for v in vals_sk],
                               textposition="outside"))
        fig.update_layout(title_text="Column Skewness", **LAYOUT)
        fig.add_hline(y=1,  line_dash="dash", line_color=ORANGE, annotation_text="Moderate skew")
        fig.add_hline(y=-1, line_dash="dash", line_color=ORANGE)
        charts.append({"title": "Skewness", "fig": fig})

    return charts