"""One-click EDA story generator with GPT + local fallback."""

from __future__ import annotations

from typing import Optional

import pandas as pd


def _local_eda_story(df: pd.DataFrame, insights: dict, audit_log: list[str]) -> str:
    """Create a beginner-friendly EDA narrative without external APIs."""
    rows, cols = df.shape
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(exclude="number").columns.tolist()
    missing_total = int(df.isna().sum().sum())
    duplicate_count = int(df.duplicated().sum())

    correlations = insights.get("strong_correlations", []) or []
    skewed = insights.get("skewed_columns", {}) or {}
    bias_warnings = insights.get("bias_warnings", []) or []

    story_lines: list[str] = []
    story_lines.append("## One-Click EDA Story")
    story_lines.append("")
    story_lines.append("### Quick Pointwise Summary")
    story_lines.append(
        f"- Dataset size: **{rows:,} rows** and **{cols} columns** "
        f"({len(numeric_cols)} numeric, {len(cat_cols)} categorical)."
    )
    story_lines.append(
        f"- Current data quality: **{missing_total} missing values** and "
        f"**{duplicate_count} duplicate rows** in the analysed table."
    )

    if audit_log:
        story_lines.append("- Recent cleaning actions:")
        for action in audit_log[-3:]:
            story_lines.append(f"  - {action}")

    if correlations:
        top = max(correlations, key=lambda x: abs(float(x.get("correlation", 0))))
        sign = "positive" if float(top.get("correlation", 0)) >= 0 else "negative"
        story_lines.append(
            f"- Strongest pattern: **{top.get('col_a', '?')}** vs "
            f"**{top.get('col_b', '?')}** with a **{sign} correlation** "
            f"(r = {float(top.get('correlation', 0)):.2f})."
        )
    else:
        story_lines.append("- No strong pairwise correlations were detected.")

    if skewed:
        top_sk_col, top_sk_val = max(skewed.items(), key=lambda item: abs(float(item[1])))
        direction = "right-skewed" if float(top_sk_val) > 0 else "left-skewed"
        story_lines.append(
            f"- Most skewed feature: **{top_sk_col}** ({direction}, skewness = {float(top_sk_val):.2f})."
        )
    else:
        story_lines.append("- No major skewness issues were detected.")

    if bias_warnings:
        story_lines.append("- Fairness note: potential bias indicators were flagged in the audit.")

    story_lines.append("")
    story_lines.append("### Detailed Brief EDA")
    story_lines.append("#### Data Quality Snapshot")
    story_lines.append(
        f"This cleaned dataset has **{rows:,} rows** and **{cols} columns**, with "
        f"**{missing_total} missing values** and **{duplicate_count} duplicate rows** currently present. "
        "This gives a quick confidence check on cleaning outcomes before deeper interpretation."
    )
    story_lines.append("")
    story_lines.append("#### Key Patterns")
    if correlations:
        story_lines.append(
            "At least one strong correlation appears in the data, which can reveal meaningful relationships "
            "between variables and guide feature selection."
        )
    else:
        story_lines.append(
            "No strong linear correlations stand out, so useful signal may be weaker, distributed, or non-linear."
        )
    if skewed:
        story_lines.append(
            "Skewness is present in key variables, so transformation or robust modeling techniques may improve results."
        )
    else:
        story_lines.append(
            "Major distributions look reasonably balanced, reducing the urgency for heavy transformation."
        )
    story_lines.append("")
    story_lines.append("#### Business/Practical Meaning")
    story_lines.append(
        "These patterns suggest where variables move together and where distributions are uneven. "
        "In practice, that helps you identify which features are likely informative, which ones may "
        "need transformation, and where data quality could affect model reliability."
    )

    story_lines.append("")
    story_lines.append("#### Recommended Next Actions")
    actions = [
        "Validate flagged quality issues against domain context before modelling.",
        "Investigate the strongest correlated variables for useful business signals.",
        "Apply scaling or transformation for highly skewed numeric columns when needed.",
        "Re-run this analysis after new data arrives to track drift over time.",
    ]
    for action in actions:
        story_lines.append(f"- {action}")

    return "\n".join(story_lines)


def generate_eda_story(
    df: pd.DataFrame,
    insights: dict,
    audit_log: list[str],
    *,
    use_gpt: bool = False,
    client: Optional[object] = None,
) -> tuple[str, str, str]:
    """
    Return a short EDA narrative.
    Uses GPT when available; falls back to local summary on any failure.
    Returns: (story_markdown, mode, detail)
    where mode is "gpt" or "local", and detail explains source/reason.
    """
    local_story = _local_eda_story(df, insights, audit_log)
    if not use_gpt or client is None:
        return local_story, "local", "No GPT client detected."

    prompt = f"""
You are an expert but beginner-friendly data analyst.
Create a short, practical "One-Click EDA Story" in plain English.
Use this exact section structure:
1) Quick Pointwise Summary (bullet points)
2) Detailed Brief EDA
   - Data Quality Snapshot
   - Key Patterns
   - Business/Practical Meaning
   - Recommended Next Actions

Rules:
- Be concise and clear for non-technical users.
- Include BOTH pointwise bullets and short explanatory paragraphs.
- Do not invent numbers.
- Keep it under 320 words.

Dataset summary:
- Shape: {df.shape[0]} rows x {df.shape[1]} columns
- Insights: {insights}
- Recent cleaning audit entries: {audit_log[-5:]}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You write concise, reliable EDA narratives for beginners.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=380,
        )
        content = response.choices[0].message.content
        if not content or not content.strip():
            return local_story, "local", "GPT returned empty content."
        return content.strip(), "gpt", "Generated via OpenAI GPT-4."
    except Exception as exc:
        return local_story, "local", f"GPT unavailable ({type(exc).__name__})."
