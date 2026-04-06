# agents/nl_query.py
# Agent 6 — Natural Language Data Querying

import pandas as pd
import numpy as np
import re


# ── Built-in query engine (no API key needed) ─────────────────────────────
def parse_and_execute(df: pd.DataFrame, question: str) -> dict:
    """
    Parses a natural language question and executes it against the dataframe.
    Returns answer, code used, and result dataframe if applicable.
    """
    q = question.lower().strip()
    result = {
        "question": question,
        "answer": None,
        "code": None,
        "dataframe": None,
        "chart_data": None,
        "error": None,
    }

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    all_cols = df.columns.tolist()

    # Find any column mentioned in the question
    def find_col(text, cols):
        for col in cols:
            if col.lower().replace("_", " ") in text or col.lower() in text:
                return col
        return None

    target_col = find_col(q, all_cols)

    try:
        # ── HOW MANY ROWS ─────────────────────────────────────────────────
        if any(x in q for x in ["how many rows", "row count", "number of rows", "total rows"]):
            result["answer"] = f"The dataset has **{len(df):,} rows**."
            result["code"] = "len(df)"

        # ── HOW MANY COLUMNS ─────────────────────────────────────────────
        elif any(x in q for x in ["how many columns", "column count", "number of columns"]):
            result["answer"] = f"The dataset has **{len(df.columns)} columns**: {', '.join(df.columns.tolist())}"
            result["code"] = "len(df.columns)"

        # ── MISSING VALUES ────────────────────────────────────────────────
        elif any(x in q for x in ["missing", "null", "nan", "empty"]):
            missing = df.isnull().sum()
            missing = missing[missing > 0]
            if missing.empty:
                result["answer"] = "✅ No missing values found in the dataset."
            else:
                result["answer"] = f"Found missing values in {len(missing)} columns:\n" + \
                    "\n".join([f"- **{col}**: {count:,} missing ({100*count/len(df):.1f}%)"
                               for col, count in missing.items()])
            result["code"] = "df.isnull().sum()"

        # ── DUPLICATES ────────────────────────────────────────────────────
        elif any(x in q for x in ["duplicate", "duplicates"]):
            dupes = df.duplicated().sum()
            result["answer"] = f"Found **{dupes:,} duplicate rows** in the dataset." if dupes > 0 \
                else "✅ No duplicate rows found."
            result["code"] = "df.duplicated().sum()"

        # ── AVERAGE / MEAN ────────────────────────────────────────────────
        elif any(x in q for x in ["average", "mean"]):
            if target_col and target_col in numeric_cols:
                val = df[target_col].mean()
                result["answer"] = f"The average of **{target_col}** is **{val:,.4f}**"
                result["code"] = f"df['{target_col}'].mean()"
            else:
                means = df[numeric_cols].mean().round(4)
                result["answer"] = "Average values for all numeric columns:\n" + \
                    "\n".join([f"- **{col}**: {val:,.4f}" for col, val in means.items()])
                result["code"] = "df.mean()"
                result["dataframe"] = means.reset_index().rename(
                    columns={"index": "Column", 0: "Mean"})

        # ── MAX ───────────────────────────────────────────────────────────
        elif any(x in q for x in ["maximum", "max", "highest", "largest"]):
            if target_col and target_col in numeric_cols:
                val = df[target_col].max()
                idx = df[target_col].idxmax()
                result["answer"] = f"The maximum value of **{target_col}** is **{val:,.4f}** (row {idx})"
                result["code"] = f"df['{target_col}'].max()"
            else:
                maxes = df[numeric_cols].max().round(4)
                result["answer"] = "Maximum values:\n" + \
                    "\n".join([f"- **{col}**: {val:,.4f}" for col, val in maxes.items()])
                result["code"] = "df.max()"

        # ── MIN ───────────────────────────────────────────────────────────
        elif any(x in q for x in ["minimum", "min", "lowest", "smallest"]):
            if target_col and target_col in numeric_cols:
                val = df[target_col].min()
                result["answer"] = f"The minimum value of **{target_col}** is **{val:,.4f}**"
                result["code"] = f"df['{target_col}'].min()"
            else:
                mins = df[numeric_cols].min().round(4)
                result["answer"] = "Minimum values:\n" + \
                    "\n".join([f"- **{col}**: {val:,.4f}" for col, val in mins.items()])
                result["code"] = "df.min()"

        # ── CORRELATION ───────────────────────────────────────────────────
        elif any(x in q for x in ["correlat", "relationship", "related"]):
            if len(numeric_cols) > 1:
                corr = df[numeric_cols].corr().round(3)
                pairs = []
                cols = corr.columns.tolist()
                for i in range(len(cols)):
                    for j in range(i+1, len(cols)):
                        val = corr.iloc[i, j]
                        if abs(val) > 0.3:
                            pairs.append((cols[i], cols[j], val))
                pairs.sort(key=lambda x: abs(x[2]), reverse=True)

                if pairs:
                    result["answer"] = f"Found **{len(pairs)} notable correlations**:\n" + \
                        "\n".join([f"- **{a}** ↔ **{b}**: {'positive' if v > 0 else 'negative'} (r = {v:.3f})"
                                   for a, b, v in pairs[:8]])
                else:
                    result["answer"] = "No strong correlations (|r| > 0.3) found between columns."
                result["code"] = "df.corr()"
            else:
                result["answer"] = "Need at least 2 numeric columns to compute correlations."

        # ── UNIQUE VALUES ─────────────────────────────────────────────────
        elif any(x in q for x in ["unique", "distinct", "different values"]):
            if target_col:
                vals = df[target_col].nunique()
                top = df[target_col].value_counts().head(5)
                result["answer"] = f"**{target_col}** has **{vals:,} unique values**.\n\nTop 5:\n" + \
                    "\n".join([f"- {v}: {c:,}" for v, c in top.items()])
                result["code"] = f"df['{target_col}'].value_counts()"
                result["dataframe"] = df[target_col].value_counts().head(10).reset_index()
                result["chart_data"] = {"type": "bar", "col": target_col,
                                        "data": df[target_col].value_counts().head(10)}
            else:
                uniques = df.nunique()
                result["answer"] = "Unique value counts per column:\n" + \
                    "\n".join([f"- **{col}**: {n:,}" for col, n in uniques.items()])
                result["code"] = "df.nunique()"

        # ── DISTRIBUTION / SUMMARY ────────────────────────────────────────
        elif any(x in q for x in ["distribution", "summary", "describe", "statistics", "stats"]):
            if target_col and target_col in numeric_cols:
                desc = df[target_col].describe().round(4)
                result["answer"] = f"Summary statistics for **{target_col}**:\n" + \
                    "\n".join([f"- **{k}**: {v:,.4f}" for k, v in desc.items()])
                result["code"] = f"df['{target_col}'].describe()"
                result["chart_data"] = {"type": "hist", "col": target_col, "data": df[target_col]}
            else:
                desc = df.describe().round(3)
                result["answer"] = "Full statistical summary computed. See table below."
                result["code"] = "df.describe()"
                result["dataframe"] = desc.reset_index().rename(columns={"index": "Stat"})

        # ── TOP N ─────────────────────────────────────────────────────────
        elif any(x in q for x in ["top", "highest", "best"]):
            n_match = re.search(r'\d+', q)
            n = int(n_match.group()) if n_match else 5
            if target_col and target_col in numeric_cols:
                top_df = df.nlargest(n, target_col)
                result["answer"] = f"Top {n} rows by **{target_col}**:"
                result["code"] = f"df.nlargest({n}, '{target_col}')"
                result["dataframe"] = top_df.head(n)
            else:
                result["answer"] = f"Showing first {n} rows of the dataset:"
                result["code"] = f"df.head({n})"
                result["dataframe"] = df.head(n)

        # ── COUNT / FILTER ────────────────────────────────────────────────
        elif any(x in q for x in ["count", "how many"]):
            if target_col and target_col in cat_cols:
                vc = df[target_col].value_counts()
                result["answer"] = f"Value counts for **{target_col}**:\n" + \
                    "\n".join([f"- {v}: {c:,}" for v, c in vc.head(10).items()])
                result["code"] = f"df['{target_col}'].value_counts()"
                result["dataframe"] = vc.head(10).reset_index()
                result["chart_data"] = {"type": "bar", "col": target_col, "data": vc.head(10)}
            else:
                result["answer"] = f"The dataset contains **{len(df):,} rows** and **{len(df.columns)} columns**."
                result["code"] = "len(df)"

        # ── OUTLIERS ─────────────────────────────────────────────────────
        elif any(x in q for x in ["outlier", "outliers", "anomal"]):
            outlier_info = []
            for col in numeric_cols:
                Q1, Q3 = df[col].quantile(0.25), df[col].quantile(0.75)
                IQR = Q3 - Q1
                n_out = ((df[col] < Q1 - 1.5*IQR) | (df[col] > Q3 + 1.5*IQR)).sum()
                if n_out > 0:
                    outlier_info.append((col, n_out))
            if outlier_info:
                result["answer"] = f"Found outliers in **{len(outlier_info)} columns**:\n" + \
                    "\n".join([f"- **{col}**: {n:,} outliers" for col, n in
                               sorted(outlier_info, key=lambda x: x[1], reverse=True)])
            else:
                result["answer"] = "✅ No significant outliers detected."
            result["code"] = "IQR outlier detection"

        # ── SHAPE ────────────────────────────────────────────────────────
        elif any(x in q for x in ["shape", "size", "dimensions"]):
            result["answer"] = f"Dataset shape: **{df.shape[0]:,} rows × {df.shape[1]} columns**"
            result["code"] = "df.shape"

        # ── COLUMNS LIST ─────────────────────────────────────────────────
        elif any(x in q for x in ["column", "columns", "features", "fields"]):
            result["answer"] = f"The dataset has **{len(df.columns)} columns**:\n" + \
                "\n".join([f"- **{col}** ({df[col].dtype})" for col in df.columns])
            result["code"] = "df.columns"

        # ── FALLBACK ─────────────────────────────────────────────────────
        else:
            result["answer"] = (
                "I couldn't interpret that question. Try asking:\n"
                "- *How many rows are there?*\n"
                "- *What is the average of [column]?*\n"
                "- *Show me the top 10 rows by [column]*\n"
                "- *Are there any missing values?*\n"
                "- *What are the correlations?*\n"
                "- *Show me the distribution of [column]*\n"
                "- *How many unique values in [column]?*"
            )

    except Exception as e:
        result["error"] = str(e)
        result["answer"] = f"Error processing query: {str(e)}"

    return result


def nl_query_gpt(df: pd.DataFrame, question: str, client) -> dict:
    """GPT-4 powered natural language query — more powerful, requires API key."""
    import json

    schema = {col: str(dtype) for col, dtype in df.dtypes.items()}
    sample = df.head(3).to_dict(orient="records")

    prompt = f"""You are a Python/Pandas data analyst. Given this dataframe schema and sample data,
answer the user's question by writing and mentally executing Pandas code.

Schema: {json.dumps(schema)}
Sample rows: {json.dumps(sample, default=str)}

Question: {question}

Respond with:
1. A clear, concise answer in plain English
2. The Pandas code you would use to get this answer

Format:
ANSWER: [your answer]
CODE: [pandas code]"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=500
    )

    content = response.choices[0].message.content
    answer, code = content, ""

    if "ANSWER:" in content:
        parts = content.split("CODE:")
        answer = parts[0].replace("ANSWER:", "").strip()
        code = parts[1].strip() if len(parts) > 1 else ""

    return {"question": question, "answer": answer, "code": code,
            "dataframe": None, "chart_data": None, "error": None}