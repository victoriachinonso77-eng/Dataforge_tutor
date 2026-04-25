# agents/intent_router.py
# GPT-4 powered intent router — reads user message and decides which agents to run
# Also validates whether the requested task is feasible with the uploaded dataset

import json
import pandas as pd

AGENT_DESCRIPTIONS = {
    "clean":     "Data cleaning — removes duplicates, fills missing values, flags outliers",
    "analyse":   "Statistical analysis — correlations, descriptive stats, skewness, bias",
    "visualise": "Data visualisation — histograms, heatmaps, scatter plots, box plots",
    "automl":    "Machine learning — trains models to predict a target column",
    "report":    "Report writing — generates a professional analysis report",
    "bias":      "Bias audit — fairness report, proxy variables, class imbalance",
    "compare":   "Multi-dataset comparison — compares two uploaded datasets",
}

TASK_REQUIREMENTS = {
    "clean":     {"min_cols": 1,  "min_rows": 2},
    "analyse":   {"min_cols": 2,  "min_rows": 5,  "needs_numeric": True},
    "visualise": {"min_cols": 1,  "min_rows": 5},
    "automl":    {"min_cols": 2,  "min_rows": 20, "needs_numeric": True},
    "report":    {"min_cols": 1,  "min_rows": 2},
    "bias":      {"min_cols": 1,  "min_rows": 5},
    "compare":   {"needs_second_dataset": True},
}


def route_intent(user_message: str, df: pd.DataFrame,
                 client, df2: pd.DataFrame = None) -> dict:
    """
    Uses GPT-4 to understand what the user wants and returns a routing decision.
    Falls back to keyword matching if GPT-4 is unavailable.
    """
    if not client:
        return _keyword_fallback(user_message, df)

    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    cat_cols     = df.select_dtypes(include=["object"]).columns.tolist()

    system_prompt = f"""You are DataForge, an AI data science tutor agent.
A student has uploaded a dataset and sent you a message asking for help.

Dataset information:
- Shape: {df.shape[0]} rows x {df.shape[1]} columns
- All columns: {list(df.columns)[:20]}
- Numeric columns: {numeric_cols[:10]}
- Categorical columns: {cat_cols[:10]}

Available agents you can run:
{json.dumps(AGENT_DESCRIPTIONS, indent=2)}

Your job:
1. Understand what the student wants from their message
2. Select only the relevant agents for their request
3. Check if the request is feasible with this specific dataset
4. If NOT feasible (e.g. they ask for football prediction with Titanic data), explain why and suggest what IS possible
5. If automl is requested, identify the most suitable target column from the dataset

Respond ONLY with valid JSON — no markdown, no extra text:
{{
  "feasible": true,
  "agents_to_run": ["clean", "analyse"],
  "target_col": null,
  "decline_reason": null,
  "response_plan": "Friendly 2-3 sentence plan of what DataForge will do",
  "teaching_focus": "The main concept this session will teach e.g. correlation analysis"
}}

Important rules:
- Always include "clean" as the first step unless data is already confirmed clean
- Only include agents that are genuinely relevant to the request
- If the request is impossible with this dataset, set feasible=false and explain clearly
- Keep response_plan encouraging and educational in tone
- teaching_focus is one specific concept e.g. "decision trees", "outlier detection"
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_message}
            ],
            max_tokens=500,
            temperature=0.2
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(raw)
        result.setdefault("feasible", True)
        result.setdefault("agents_to_run", ["clean", "analyse"])
        result.setdefault("target_col", None)
        result.setdefault("decline_reason", None)
        result.setdefault("response_plan", "I will analyse your data now.")
        result.setdefault("teaching_focus", "data science")
        return result
    except Exception as e:
        print(f"Intent router error: {e}")
        return _keyword_fallback(user_message, df)


def validate_task(agents: list, df: pd.DataFrame,
                  target_col: str = None, df2: pd.DataFrame = None) -> dict:
    """
    Validates each requested agent against actual dataset properties.
    Returns {agent: {can_run: bool, reason: str}}
    """
    results = {}
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

    for agent in agents:
        reqs    = TASK_REQUIREMENTS.get(agent, {})
        can_run = True
        reason  = "Ready"

        if reqs.get("min_rows") and df.shape[0] < reqs["min_rows"]:
            can_run = False
            reason  = f"Needs {reqs['min_rows']}+ rows — dataset has {df.shape[0]}"

        elif reqs.get("min_cols") and df.shape[1] < reqs["min_cols"]:
            can_run = False
            reason  = f"Needs {reqs['min_cols']}+ columns"

        elif reqs.get("needs_numeric") and len(numeric_cols) == 0:
            can_run = False
            reason  = "No numeric columns found — needed for this analysis"

        elif agent == "automl":
            if target_col and target_col not in df.columns:
                can_run = False
                reason  = f"Column '{target_col}' not found in dataset"
            elif df.shape[0] < 20:
                can_run = False
                reason  = f"Need 20+ rows for ML — dataset has {df.shape[0]}"

        elif agent == "compare" and df2 is None:
            can_run = False
            reason  = "Upload a second dataset to enable comparison"

        results[agent] = {"can_run": can_run, "reason": reason}

    return results


def _keyword_fallback(message: str, df: pd.DataFrame) -> dict:
    """Keyword-based fallback when GPT-4 is unavailable."""
    msg    = message.lower()
    agents = ["clean"]

    if any(w in msg for w in ["correlat", "stat", "analys", "mean", "average", "distribution"]):
        agents.append("analyse")
    if any(w in msg for w in ["chart", "plot", "graph", "visual", "show", "histogram"]):
        agents.append("visualise")
    if any(w in msg for w in ["predict", "model", "ml", "machine", "classif", "regress", "forecast"]):
        agents.append("automl")
    if any(w in msg for w in ["report", "summary", "write", "document"]):
        agents.append("report")
    if any(w in msg for w in ["bias", "fair", "imbalanc", "equity"]):
        agents.append("bias")
    if len(agents) == 1:
        agents = ["clean", "analyse", "visualise"]

    return {
        "feasible":      True,
        "agents_to_run": agents,
        "target_col":    None,
        "decline_reason": None,
        "response_plan": f"I will run {', '.join(agents)} on your dataset and teach you what each step means.",
        "teaching_focus": "data science pipeline"
    }