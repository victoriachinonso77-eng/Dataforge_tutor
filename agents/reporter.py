# agents/reporter.py
# Agent 4 — GPT-4 Natural Language Report Writer

import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def generate_report(insights: dict, audit_log: list[str], client: OpenAI) -> str:
    summary = {
        "dataset_shape": insights.get("shape", {}),
        "columns": insights.get("columns", []),
        "numeric_summary": {
            k: {stat: val for stat, val in v.items()}
            for k, v in insights.get("numeric_summary", {}).items()
        },
        "strong_correlations": insights.get("strong_correlations", []),
        "categorical_summary": {
            col: data.get("top_5", {})
            for col, data in insights.get("categorical_summary", {}).items()
        },
        "skewed_columns": insights.get("skewed_columns", {}),
        "bias_warnings": insights.get("bias_warnings", []),
        "cleaning_log": audit_log[-5:],
    }

    prompt = f"""
You are DataForge, an expert autonomous data analyst AI.
You have just processed a dataset and gathered the following insights:

{json.dumps(summary, indent=2)}

Write a professional, structured data analysis report in Markdown.
The report must include the following sections:

1. **Executive Summary** — 2-3 sentence overview of the dataset and key findings.
2. **Dataset Overview** — Describe the size, structure and column types.
3. **Key Statistical Findings** — Highlight the most important numeric insights, distributions, and trends.
4. **Correlations & Relationships** — Describe any strong correlations found between variables.
5. **Data Quality Notes** — Summarise what was cleaned and any remaining concerns.
6. **Bias & Fairness Warnings** — Call out any skewness or potential bias issues discovered.
7. **Recommendations** — 3-5 actionable recommendations for analysts or stakeholders.

Write clearly and professionally. Use bullet points where appropriate.
Do NOT make up data that isn't in the provided insights.
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are DataForge, a professional AI data analyst. Write clear, accurate, insightful reports."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4,
        max_tokens=1500
    )

    return response.choices[0].message.content


def generate_report_fallback(insights: dict, audit_log: list[str]) -> str:
    shape = insights.get("shape", {})
    cols = insights.get("columns", [])
    numeric = insights.get("numeric_summary", {})
    correlations = insights.get("strong_correlations", [])
    categorical = insights.get("categorical_summary", {})
    skewed = insights.get("skewed_columns", {})
    bias_warnings = insights.get("bias_warnings", [])

    lines = []
    lines.append("# 📊 DataForge Analysis Report\n")
    lines.append("*Generated autonomously by DataForge AI Agent*\n")
    lines.append("---\n")

    lines.append("## 1. Executive Summary\n")
    lines.append(f"The dataset contains **{shape.get('rows', '?')} rows** and "
                 f"**{shape.get('cols', '?')} columns**. "
                 f"DataForge has autonomously cleaned, analysed and visualised this data. "
                 f"A total of **{len(cols)} features** were examined, "
                 f"with **{len(numeric)} numeric** and **{len(categorical)} categorical** columns identified.\n")

    lines.append("## 2. Dataset Overview\n")
    lines.append(f"- **Total rows:** {shape.get('rows', 'N/A')}")
    lines.append(f"- **Total columns:** {shape.get('cols', 'N/A')}")
    lines.append(f"- **Numeric columns:** {', '.join(numeric.keys()) if numeric else 'None'}")
    lines.append(f"- **Categorical columns:** {', '.join(categorical.keys()) if categorical else 'None'}\n")

    lines.append("## 3. Key Statistical Findings\n")
    if numeric:
        for col, stats in list(numeric.items())[:5]:
            lines.append(f"**{col}**: mean={stats.get('mean')}, std={stats.get('std')}, min={stats.get('min')}, max={stats.get('max')}")
        lines.append("")
    else:
        lines.append("No numeric columns found.\n")

    if skewed:
        lines.append("### Skewness Detected\n")
        for col, val in skewed.items():
            direction = "right (positively)" if val > 0 else "left (negatively)"
            lines.append(f"- `{col}` is skewed {direction} (skewness = {val})")
        lines.append("")

    lines.append("## 4. Correlations & Relationships\n")
    if correlations:
        for pair in correlations:
            strength = "strong positive" if pair["correlation"] > 0 else "strong negative"
            lines.append(f"- **{pair['col_a']}** and **{pair['col_b']}**: {strength} correlation (r = {pair['correlation']})")
        lines.append("")
    else:
        lines.append("No strong correlations (r > 0.5) were detected between numeric columns.\n")

    lines.append("## 5. Data Quality Notes\n")
    for entry in audit_log:
        lines.append(f"- {entry}")
    lines.append("")

    lines.append("## 6. Bias & Fairness Warnings\n")
    if bias_warnings:
        for w in bias_warnings:
            lines.append(f"⚠️ {w}")
    else:
        lines.append("✅ No significant bias concerns detected in this dataset.")
    lines.append("")

    lines.append("## 7. Recommendations\n")
    recs = [
        "Validate all cleaning steps against domain knowledge before using for modelling.",
        "Investigate any flagged outliers — they may represent genuine anomalies or data entry errors.",
    ]
    if correlations:
        recs.append(f"Explore the relationship between '{correlations[0]['col_a']}' and '{correlations[0]['col_b']}' further.")
    if skewed:
        recs.append(f"Consider applying log transformation to skewed columns ({', '.join(skewed.keys())}) before modelling.")
    recs.append("Run this pipeline on updated data regularly to track changes over time.")

    for i, rec in enumerate(recs, 1):
        lines.append(f"{i}. {rec}")
    lines.append("")

    lines.append("---")
    lines.append("*Report generated by DataForge — Autonomous Data Pipeline Agent*")

    return "\n".join(lines)
