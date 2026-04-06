# agents/cleaner.py
# Agent 1 — Data Cleaning & Validation

import pandas as pd
import numpy as np


def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """
    Autonomously cleans a dataframe.
    Returns the cleaned dataframe and a human-readable audit log.
    """
    log = []
    original_shape = df.shape

    # ── 1. Strip whitespace from column names ────────────────────────────────
    df.columns = df.columns.str.strip().str.replace(" ", "_").str.lower()
    log.append(f"✅ Standardised column names to snake_case.")

    # ── 2. Remove duplicate rows ─────────────────────────────────────────────
    dupes = df.duplicated().sum()
    if dupes > 0:
        df = df.drop_duplicates()
        log.append(f"🗑️  Removed {dupes} duplicate rows.")
    else:
        log.append("✅ No duplicate rows found.")

    # ── 3. Detect and drop columns that are >80% empty ───────────────────────
    threshold = 0.8
    mostly_empty = [c for c in df.columns if df[c].isnull().mean() > threshold]
    if mostly_empty:
        df = df.drop(columns=mostly_empty)
        log.append(f"🗑️  Dropped {len(mostly_empty)} columns with >80% missing values: {mostly_empty}")
    else:
        log.append("✅ No columns exceeded the 80% missing threshold.")

    # ── 4. Handle missing values ─────────────────────────────────────────────
    missing_before = df.isnull().sum().sum()
    if missing_before > 0:
        for col in df.columns:
            if df[col].isnull().sum() == 0:
                continue
            if df[col].dtype in [np.float64, np.int64, float, int]:
                median_val = df[col].median()
                df[col] = df[col].fillna(median_val)
                log.append(f"🔧 Filled missing values in '{col}' with median ({median_val:.2f}).")
            else:
                mode_val = df[col].mode()
                if not mode_val.empty:
                    df[col] = df[col].fillna(mode_val[0])
                    log.append(f"🔧 Filled missing values in '{col}' with mode ('{mode_val[0]}').")
                else:
                    df[col] = df[col].fillna("Unknown")
                    log.append(f"🔧 Filled missing values in '{col}' with 'Unknown'.")
    else:
        log.append("✅ No missing values found.")

    # ── 5. Detect and flag outliers in numeric columns ───────────────────────
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    outlier_flags = {}
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower, upper = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
        outliers = ((df[col] < lower) | (df[col] > upper)).sum()
        if outliers > 0:
            outlier_flags[col] = outliers
            log.append(f"⚠️  Detected {outliers} outliers in '{col}' (IQR method). Flagged, not removed.")

    if not outlier_flags:
        log.append("✅ No significant outliers detected.")

    # ── 6. Attempt to parse date columns ─────────────────────────────────────
    for col in df.select_dtypes(include=["object"]).columns:
        sample = df[col].dropna().head(20)
        try:
            parsed = pd.to_datetime(sample, infer_datetime_format=True, errors="coerce")
            if parsed.notna().mean() > 0.7:
                df[col] = pd.to_datetime(df[col], infer_datetime_format=True, errors="coerce")
                log.append(f"📅 Parsed '{col}' as datetime.")
        except Exception:
            pass

    # ── Summary ───────────────────────────────────────────────────────────────
    log.append(f"\n📊 Summary: {original_shape[0]} rows × {original_shape[1]} cols  →  "
               f"{df.shape[0]} rows × {df.shape[1]} cols after cleaning.")

    return df, log