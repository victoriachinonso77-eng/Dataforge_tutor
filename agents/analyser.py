# agents/analyser.py
# Agent 2 — Statistical Analysis & Insight Extraction

import pandas as pd
import numpy as np


def analyse_data(df: pd.DataFrame) -> dict:
    """
    Runs statistical analysis on cleaned dataframe.
    Returns a dict of insights used by the report agent.
    """
    insights = {}

    numeric_df = df.select_dtypes(include=[np.number])
    categorical_df = df.select_dtypes(include=["object", "category"])

    # ── Basic shape ───────────────────────────────────────────────────────────
    insights["shape"] = {"rows": df.shape[0], "cols": df.shape[1]}
    insights["columns"] = list(df.columns)
    insights["dtypes"] = df.dtypes.astype(str).to_dict()

    # ── Numeric summary ───────────────────────────────────────────────────────
    if not numeric_df.empty:
        desc = numeric_df.describe().round(3)
        insights["numeric_summary"] = desc.to_dict()

        # Correlation matrix
        if numeric_df.shape[1] > 1:
            corr = numeric_df.corr().round(3)
            insights["correlation"] = corr.to_dict()

            # Top correlated pairs
            pairs = []
            cols = corr.columns.tolist()
            for i in range(len(cols)):
                for j in range(i + 1, len(cols)):
                    val = corr.iloc[i, j]
                    if abs(val) > 0.5:
                        pairs.append({
                            "col_a": cols[i],
                            "col_b": cols[j],
                            "correlation": round(val, 3)
                        })
            pairs.sort(key=lambda x: abs(x["correlation"]), reverse=True)
            insights["strong_correlations"] = pairs[:5]

    # ── Categorical summary ───────────────────────────────────────────────────
    if not categorical_df.empty:
        cat_summary = {}
        for col in categorical_df.columns:
            vc = df[col].value_counts()
            cat_summary[col] = {
                "unique_count": int(df[col].nunique()),
                "top_5": vc.head(5).to_dict()
            }
        insights["categorical_summary"] = cat_summary

    # ── Skewness flags ────────────────────────────────────────────────────────
    skewed = {}
    for col in numeric_df.columns:
        skew_val = numeric_df[col].skew()
        if abs(skew_val) > 1:
            skewed[col] = round(skew_val, 3)
    insights["skewed_columns"] = skewed

    # ── Missing values (post-clean check) ────────────────────────────────────
    missing = df.isnull().sum()
    insights["missing_values"] = missing[missing > 0].to_dict()

    # ── Bias warning ─────────────────────────────────────────────────────────
    bias_warnings = []
    for col, skew_val in skewed.items():
        if abs(skew_val) > 2:
            bias_warnings.append(
                f"Column '{col}' is highly skewed (skewness={skew_val}). "
                "This may introduce bias in predictive models."
            )
    insights["bias_warnings"] = bias_warnings

    return insights