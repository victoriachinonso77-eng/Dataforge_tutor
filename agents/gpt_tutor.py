# agents/gpt_tutor.py
# GPT-4 Powered Tutor Agent — personalises every part of the learning experience
# Falls back to static content if no API key is available

import json
import os


def _chat(client, system: str, user: str, max_tokens: int = 600, temperature: float = 0.5) -> str:
    """Helper to call GPT-4 and return text response."""
    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"[GPT-4 unavailable: {str(e)}]"


# ── 1. PERSONALISED LESSON ─────────────────────────────────────────────────
def generate_lesson(client, stage: str, level: str,
                    dataset_context: dict) -> str:
    """
    Generates a lesson personalised to the student's actual dataset.
    dataset_context includes: shape, columns, dtypes, sample findings.
    """
    system = f"""You are a friendly, encouraging data science tutor teaching a {level} student.
Write clear, jargon-free explanations using simple analogies.
Always reference the student's actual dataset in your explanation — make it feel personal.
Use markdown formatting with headers, bold key terms, and short paragraphs.
Keep the lesson under 300 words."""

    stage_prompts = {
        "cleaning": f"""The student has uploaded a dataset with these properties:
- Shape: {dataset_context.get('shape', 'unknown')}
- Columns: {', '.join(dataset_context.get('columns', [])[:8])}
- Missing values found: {dataset_context.get('missing_count', 0)}
- Duplicate rows found: {dataset_context.get('n_duplicates', 0)}
- Outliers detected in: {', '.join(dataset_context.get('outlier_cols', [])[:4])}

Write a personalised lesson explaining what data cleaning is and why it matters,
referencing the specific issues found in THEIR dataset. Make it feel like you're 
talking about their data specifically, not a generic example.""",

        "analysis": f"""The student's dataset has been cleaned. Key findings:
- Shape: {dataset_context.get('shape', 'unknown')}
- Columns: {', '.join(dataset_context.get('columns', [])[:8])}
- Strongest correlation: {dataset_context.get('top_correlation', 'none found')}
- Most skewed column: {dataset_context.get('most_skewed', 'none')}
- Number of numeric columns: {dataset_context.get('n_numeric', 0)}

Write a personalised lesson explaining statistical analysis using findings from 
THEIR specific dataset as examples. Explain mean, median, correlation and skewness 
using numbers from their actual data.""",

        "visualisation": f"""The student's dataset has these characteristics:
- Shape: {dataset_context.get('shape', 'unknown')}  
- Numeric columns: {dataset_context.get('n_numeric', 0)}
- Categorical columns: {dataset_context.get('n_categorical', 0)}
- Charts generated: {', '.join(dataset_context.get('chart_types', []))}

Write a personalised lesson explaining why we visualise data and how to read 
the specific charts that were generated for THEIR dataset.""",

        "automl": f"""The student selected '{dataset_context.get('target_col', 'unknown')}' as 
the column to predict. DataForge detected this as a {dataset_context.get('task_type', 'unknown')} problem.
The best model was {dataset_context.get('best_model', 'unknown')} with 
{dataset_context.get('metric_name', 'accuracy')} of {dataset_context.get('best_score', 'unknown')}.

Write a personalised lesson explaining machine learning using their specific prediction 
task as the example. Explain why this is classification or regression, and what it 
means to predict '{dataset_context.get('target_col', 'this column')}'.""",
    }

    user = stage_prompts.get(stage, f"Write a lesson about {stage} in data science.")
    return _chat(client, system, user, max_tokens=500)


# ── 2. PERSONALISED QUIZ QUESTIONS ────────────────────────────────────────
def generate_quiz(client, stage: str, level: str,
                  dataset_context: dict) -> list[dict]:
    """
    Generates quiz questions personalised to the student's actual dataset findings.
    Returns a list of {q, options, answer, explanation} dicts.
    """
    system = f"""You are a data science tutor creating quiz questions for a {level} student.
Create questions based on the student's ACTUAL dataset findings — not generic examples.
Return ONLY a valid JSON array. No markdown, no preamble, no extra text.
Each item must have: "q" (question string), "options" (array of 4 strings), 
"answer" (integer 0-3 for correct option index), "explanation" (string explaining why)."""

    stage_prompts = {
        "cleaning": f"""Dataset context:
- Missing values: {dataset_context.get('missing_count', 0)} found
- Duplicates removed: {dataset_context.get('n_duplicates', 0)}
- Outliers flagged in: {', '.join(dataset_context.get('outlier_cols', [])[:3])}
- Imputation used: median for numeric, mode for categorical

Create 2 quiz questions about data cleaning concepts, referencing these specific findings.""",

        "analysis": f"""Dataset context:
- Top correlation: {dataset_context.get('top_correlation', 'none')} (r={dataset_context.get('top_corr_val', 0)})
- Most skewed column: {dataset_context.get('most_skewed', 'none')} (skew={dataset_context.get('skew_val', 0)})
- Number of rows: {dataset_context.get('n_rows', 0)}

Create 2 quiz questions about statistical analysis referencing these specific findings.""",

        "visualisation": f"""Dataset context:
- Charts generated: {', '.join(dataset_context.get('chart_types', ['histogram', 'heatmap']))}
- Strongest correlation visible: {dataset_context.get('top_correlation', 'none')}
- Distribution shape of main column: {dataset_context.get('dist_shape', 'unknown')}

Create 2 quiz questions about reading and interpreting the charts generated.""",

        "automl": f"""Dataset context:
- Target column: {dataset_context.get('target_col', 'unknown')}
- Task type: {dataset_context.get('task_type', 'classification')}
- Best model: {dataset_context.get('best_model', 'Random Forest')}
- Best score: {dataset_context.get('best_score', 0.85)}
- Worst model: {dataset_context.get('worst_model', 'unknown')}

Create 2 quiz questions about machine learning referencing these specific results.""",
    }

    user = stage_prompts.get(stage, f"Create 2 quiz questions about {stage}.")

    raw = _chat(client, system, user, max_tokens=800, temperature=0.4)

    try:
        # Strip any accidental markdown
        clean = raw.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        questions = json.loads(clean)
        # Validate structure
        validated = []
        for q in questions:
            if all(k in q for k in ["q", "options", "answer", "explanation"]):
                if isinstance(q["options"], list) and len(q["options"]) == 4:
                    if isinstance(q["answer"], int) and 0 <= q["answer"] <= 3:
                        validated.append(q)
        return validated if validated else _fallback_quiz(stage)
    except Exception:
        return _fallback_quiz(stage)


def _fallback_quiz(stage: str) -> list[dict]:
    """Returns simple fallback questions if GPT-4 JSON parsing fails."""
    fallbacks = {
        "cleaning": [{
            "q": "Why do we use the median to fill missing numeric values?",
            "options": ["It is the largest value", "It is resistant to outliers",
                        "It is always the most common value", "It is faster to calculate"],
            "answer": 1,
            "explanation": "The median is the middle value when sorted — extreme values don't affect it, making it robust for skewed data."
        }],
        "analysis": [{
            "q": "What does a correlation of r = -0.8 mean?",
            "options": ["No relationship", "Weak positive relationship",
                        "Strong negative relationship", "Perfect positive relationship"],
            "answer": 2,
            "explanation": "r = -0.8 is a strong negative correlation — as one variable increases, the other tends to decrease significantly."
        }],
        "visualisation": [{
            "q": "What does a long right tail in a histogram indicate?",
            "options": ["Normal distribution", "Negative skewness",
                        "Positive skewness", "No variance"],
            "answer": 2,
            "explanation": "A long right tail means positive skewness — most values are low but a few are very high."
        }],
        "automl": [{
            "q": "What does cross-validation help us avoid?",
            "options": ["Slow training", "Overfitting to training data",
                        "Too many features", "Missing values"],
            "answer": 1,
            "explanation": "Cross-validation tests the model on multiple different subsets of data, giving a more reliable performance estimate."
        }],
    }
    return fallbacks.get(stage, [])


# ── 3. AUDIT LOG EXPLANATION ───────────────────────────────────────────────
def explain_audit_log(client, audit_log: list[str], level: str,
                      dataset_name: str = "your dataset") -> str:
    """
    GPT-4 explains the cleaning audit log in plain English.
    """
    system = f"""You are a friendly data science tutor explaining data cleaning results 
to a {level} student. Be encouraging and specific. Use simple language.
Reference the actual numbers and columns mentioned. Keep under 200 words.
Use markdown with bullet points."""

    user = f"""The student's dataset '{dataset_name}' was just cleaned. 
Here is the complete audit trail of what happened:

{chr(10).join(audit_log)}

Explain what happened in plain English, why each step was necessary, 
and what it means for the quality of their data now."""

    return _chat(client, system, user, max_tokens=350)


# ── 4. CHART INTERPRETATION ────────────────────────────────────────────────
def interpret_chart(client, chart_title: str, chart_type: str,
                    level: str, insights: dict) -> str:
    """
    GPT-4 tells the student what their specific chart means.
    """
    system = f"""You are a data science tutor helping a {level} student understand 
their data visualisation. Be specific, practical and encouraging.
Explain what the chart reveals about THEIR actual data. Under 150 words.
Use markdown."""

    # Build context from insights
    correlations = insights.get("strong_correlations", [])
    skewed = insights.get("skewed_columns", {})
    bias_warnings = insights.get("bias_warnings", [])

    context_parts = []
    if correlations:
        top = correlations[0]
        context_parts.append(f"Strongest correlation: {top['col_a']} vs {top['col_b']} (r={top['correlation']})")
    if skewed:
        top_sk = list(skewed.items())[0]
        context_parts.append(f"Most skewed column: {top_sk[0]} (skewness={top_sk[1]:.2f})")
    if bias_warnings:
        context_parts.append(f"Bias warnings: {bias_warnings[0]}")

    context = "\n".join(context_parts) if context_parts else "General dataset analysis"

    user = f"""The student is looking at a {chart_type} titled '{chart_title}'.
Dataset context:
{context}

Tell the student:
1. What this specific chart is showing them about their data
2. What the most important thing to notice is
3. What action they might consider based on what they see"""

    return _chat(client, system, user, max_tokens=250)


# ── 5. PERSONALISED QUIZ FEEDBACK ─────────────────────────────────────────
def generate_feedback(client, stage: str, level: str,
                      score: int, total: int,
                      wrong_questions: list[str]) -> str:
    """
    GPT-4 gives personalised feedback based on quiz performance.
    """
    system = f"""You are an encouraging data science tutor giving feedback to a {level} student.
Be warm, specific and constructive. Keep under 150 words. Use markdown."""

    pct = int((score / total) * 100) if total > 0 else 0

    if wrong_questions:
        wrong_str = "\n".join(f"- {q}" for q in wrong_questions[:3])
        user = f"""The student just completed the {stage} quiz.
Score: {score}/{total} ({pct}%)
Questions they got wrong:
{wrong_str}

Give personalised feedback on their performance and specific advice 
on the concepts they struggled with. Be encouraging."""
    else:
        user = f"""The student just scored {score}/{total} ({pct}%) on the {stage} quiz.
They got all questions correct!
Give a brief encouraging message and tell them what to focus on next."""

    return _chat(client, system, user, max_tokens=200)


# ── 6. AUTOML EXPLANATION ─────────────────────────────────────────────────
def explain_automl_results(client, ml_results: dict, level: str) -> str:
    """
    GPT-4 explains the AutoML results in plain English based on actual findings.
    """
    system = f"""You are a data science tutor explaining machine learning results 
to a {level} student. Be specific about their actual results. 
Avoid jargon — use plain English and analogies. Under 250 words. Use markdown."""

    models = ml_results.get("models", [])
    model_summary = "\n".join(
        [f"- {m['name']}: {m['score']:.1%} {ml_results.get('best_metric','accuracy')}"
         for m in models[:5]]
    )

    fi = ml_results.get("feature_importance", {})
    top_features = list(fi.items())[:3] if fi else []
    feature_str = ", ".join([f"{k} ({v:.2%})" for k, v in top_features]) if top_features else "not available"

    user = f"""DataForge just ran AutoML on the student's dataset. Here are the results:

Target column: {ml_results.get('target_col', 'unknown')}
Task type: {ml_results.get('task_type', 'unknown')}
Best model: {ml_results.get('best_model', 'unknown')}
Best score: {ml_results.get('best_score', 0):.1%} ({ml_results.get('best_metric', 'accuracy')})
Trained on: {ml_results.get('n_samples', 0):,} samples with {ml_results.get('n_features', 0)} features
Top features: {feature_str}

All model results:
{model_summary}

Explain to the student:
1. What the best model found and what that score means in plain English
2. Why it beat the other models (in simple terms)  
3. What the top features tell us about which columns matter most
4. One practical thing they could do next to improve the model"""

    return _chat(client, system, user, max_tokens=400)


# ── 7. CONTEXT BUILDER ────────────────────────────────────────────────────
def build_dataset_context(df, insights: dict, audit_log: list = None,
                          ml_results: dict = None) -> dict:
    """
    Builds a context dictionary from the actual dataset and pipeline results.
    Used to personalise all GPT-4 calls.
    """
    import numpy as np

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    # Top correlation
    correlations = insights.get("strong_correlations", [])
    top_corr = correlations[0] if correlations else {}

    # Most skewed
    skewed = insights.get("skewed_columns", {})
    most_skewed = max(skewed.items(), key=lambda x: abs(x[1])) if skewed else (None, 0)

    # Outlier columns from audit log
    outlier_cols = []
    if audit_log:
        for entry in audit_log:
            if "outlier" in entry.lower() and "'" in entry:
                try:
                    col = entry.split("'")[1]
                    outlier_cols.append(col)
                except:
                    pass

    # Missing count
    missing_count = df.isnull().sum().sum()

    # Duplicates from audit
    n_dupes = 0
    if audit_log:
        for entry in audit_log:
            if "duplicate" in entry.lower():
                import re
                nums = re.findall(r'\d+', entry)
                if nums:
                    n_dupes = int(nums[0])
                    break

    ctx = {
        "shape":           f"{df.shape[0]:,} rows × {df.shape[1]} columns",
        "columns":         df.columns.tolist(),
        "n_numeric":       len(numeric_cols),
        "n_categorical":   len(cat_cols),
        "n_rows":          df.shape[0],
        "missing_count":   int(missing_count),
        "n_duplicates":    n_dupes,
        "outlier_cols":    outlier_cols,
        "top_correlation": f"{top_corr.get('col_a','?')} vs {top_corr.get('col_b','?')}" if top_corr else "none found",
        "top_corr_val":    top_corr.get("correlation", 0),
        "most_skewed":     most_skewed[0] or "none",
        "skew_val":        round(most_skewed[1], 2),
        "dist_shape":      "right-skewed" if most_skewed[1] > 1 else "left-skewed" if most_skewed[1] < -1 else "roughly normal",
        "bias_warnings":   insights.get("bias_warnings", []),
    }

    if ml_results:
        ctx.update({
            "target_col":  ml_results.get("target_col", "unknown"),
            "task_type":   ml_results.get("task_type", "unknown"),
            "best_model":  ml_results.get("best_model", "unknown"),
            "best_score":  f"{ml_results.get('best_score', 0):.1%}",
            "metric_name": ml_results.get("best_metric", "accuracy"),
            "worst_model": ml_results["models"][-1]["name"] if ml_results.get("models") else "unknown",
        })

    return ctx