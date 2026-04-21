# agents/visualiser.py
# Agent 3 — Intelligent Chart Generation

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
import seaborn as sns
import io
import base64

# Style
sns.set_theme(style="whitegrid")
PALETTE = ["#02C39A", "#028090", "#F77F00", "#E63946", "#5A67D8", "#38A169"]


def fig_to_base64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=130)
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return encoded


def generate_charts(df: pd.DataFrame, insights: dict) -> list[dict]:
    """
    Intelligently selects and generates charts based on data shape.
    Returns list of {"title": str, "b64": str} dicts.
    """
    charts = []
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    # ── 1. Distribution histograms for numeric columns ────────────────────────
    if numeric_cols:
        n = min(len(numeric_cols), 4)
        cols_to_plot = numeric_cols[:n]
        fig, axes = plt.subplots(1, n, figsize=(5 * n, 4))
        if n == 1:
            axes = [axes]
        for ax, col in zip(axes, cols_to_plot):
            ax.hist(df[col].dropna(), bins=20, color=PALETTE[0], edgecolor="white", alpha=0.85)
            ax.set_title(col.replace("_", " ").title(), fontsize=12, fontweight="bold")
            ax.set_xlabel("Value")
            ax.set_ylabel("Frequency")
        fig.suptitle("Distributions of Numeric Columns", fontsize=14, fontweight="bold", y=1.02)
        charts.append({"title": "Numeric Distributions", "b64": fig_to_base64(fig)})

    # ── 2. Correlation heatmap ────────────────────────────────────────────────
    if len(numeric_cols) > 1:
        corr = df[numeric_cols].corr()
        fig, ax = plt.subplots(figsize=(max(6, len(numeric_cols)), max(5, len(numeric_cols) - 1)))
        mask = np.triu(np.ones_like(corr, dtype=bool))
        sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="RdYlGn",
                    center=0, ax=ax, linewidths=0.5, annot_kws={"size": 10})
        ax.set_title("Correlation Heatmap", fontsize=14, fontweight="bold")
        charts.append({"title": "Correlation Heatmap", "b64": fig_to_base64(fig)})

    # ── 3. Top category bar charts ────────────────────────────────────────────
    for col in categorical_cols[:2]:
        vc = df[col].value_counts().head(8)
        fig, ax = plt.subplots(figsize=(8, 4))
        bars = ax.barh(vc.index.astype(str), vc.values,
                       color=PALETTE[:len(vc)], edgecolor="white")
        ax.set_title(f"Top Values — {col.replace('_', ' ').title()}", fontsize=13, fontweight="bold")
        ax.set_xlabel("Count")
        for bar, val in zip(bars, vc.values):
            ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                    str(val), va="center", fontsize=10)
        fig.tight_layout()
        charts.append({"title": f"Category Breakdown: {col}", "b64": fig_to_base64(fig)})

    # ── 4. Box plots for outlier visualisation ────────────────────────────────
    if numeric_cols:
        n = min(len(numeric_cols), 4)
        fig, ax = plt.subplots(figsize=(max(6, n * 2), 5))
        df[numeric_cols[:n]].boxplot(ax=ax, patch_artist=True,
            boxprops=dict(facecolor=PALETTE[0], color=PALETTE[1]),
            medianprops=dict(color=PALETTE[2], linewidth=2),
            whiskerprops=dict(color=PALETTE[1]),
            capprops=dict(color=PALETTE[1]))
        ax.set_title("Outlier Detection — Box Plots", fontsize=13, fontweight="bold")
        ax.set_ylabel("Value")
        plt.xticks(rotation=30, ha="right")
        fig.tight_layout()
        charts.append({"title": "Outlier Detection", "b64": fig_to_base64(fig)})

    # ── 5. Missing values bar (if any pre-clean data was passed) ─────────────
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if not missing.empty:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(missing.index, missing.values, color=PALETTE[3], edgecolor="white")
        ax.set_title("Remaining Missing Values", fontsize=13, fontweight="bold")
        ax.set_ylabel("Count")
        plt.xticks(rotation=30, ha="right")
        fig.tight_layout()
        charts.append({"title": "Missing Values", "b64": fig_to_base64(fig)})

    # ── 6. Scatter plot for top correlated pair ───────────────────────────────
    strong = insights.get("strong_correlations", [])
    if strong:
        top = strong[0]
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.scatter(df[top["col_a"]], df[top["col_b"]],
                   alpha=0.6, color=PALETTE[0], edgecolors=PALETTE[1], s=50)
        ax.set_xlabel(top["col_a"].replace("_", " ").title())
        ax.set_ylabel(top["col_b"].replace("_", " ").title())
        ax.set_title(f"Scatter: {top['col_a']} vs {top['col_b']}  (r={top['correlation']})",
                     fontsize=12, fontweight="bold")
        fig.tight_layout()
        charts.append({"title": f"Scatter Plot (r={top['correlation']})", "b64": fig_to_base64(fig)})

    return charts