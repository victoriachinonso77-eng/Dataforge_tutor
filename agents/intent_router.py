# agents/intent_router.py
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


def route_intent(user_message, df, client=None, df2=None):
    """Routes user message to relevant agents. Falls back to keywords if GPT-4 fails."""
    if client:
        try:
            numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
            cat_cols     = df.select_dtypes(include=["object"]).columns.tolist()

            system_prompt = f"""You are DataForge, an AI data science tutor agent.
A student has uploaded a dataset and sent you a message.

Dataset: {df.shape[0]} rows x {df.shape[1]} columns
All columns: {list(df.columns)[:20]}
Numeric columns: {numeric_cols[:10]}
Categorical columns: {cat_cols[:10]}

Available agents: {json.dumps(AGENT_DESCRIPTIONS)}

Respond ONLY with valid JSON:
{{
  "feasible": true,
  "agents_to_run": ["clean", "analyse"],
  "target_col": null,
  "decline_reason": null,
  "response_plan": "Friendly 2-3 sentence plan",
  "teaching_focus": "main concept e.g. correlation analysis"
}}

If the request is impossible with this dataset, set feasible=false and explain why.
Always include clean as first step."""

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
            print(f"GPT-4 routing failed ({e}), using keyword fallback")

    # Always fall back to keywords — works without any API key
    return _keyword_fallback(user_message, df)


def validate_task(agents, df, target_col=None, df2=None):
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
            reason  = "No numeric columns found"
        elif agent == "automl":
            if target_col and target_col not in df.columns:
                can_run = False
                reason  = f"Column '{target_col}' not found"
            elif df.shape[0] < 20:
                can_run = False
                reason  = f"Need 20+ rows for ML"
        elif agent == "compare" and df2 is None:
            can_run = False
            reason  = "Upload a second dataset to enable comparison"

        results[agent] = {"can_run": can_run, "reason": reason}
    return results


def _keyword_fallback(message, df):
    msg    = message.lower()
    agents = ["clean"]

    if any(w in msg for w in ["stat", "analys", "correlat", "mean", "average", "distribution", "number"]):
        agents.append("analyse")
    if any(w in msg for w in ["chart", "plot", "graph", "visual", "show", "histogram", "see"]):
        agents.append("visualise")
    if any(w in msg for w in ["predict", "model", "ml", "machine", "classif", "regress", "forecast"]):
        agents.append("automl")
    if any(w in msg for w in ["report", "summary", "write", "document", "full analysis"]):
        agents.append("report")
        agents.append("analyse")
        agents.append("visualise")
    if any(w in msg for w in ["bias", "fair", "imbalanc", "equity"]):
        agents.append("bias")
    if len(agents) == 1:
        agents = ["clean", "analyse", "visualise"]

    # Remove duplicates while preserving order
    seen = set()
    agents = [a for a in agents if not (a in seen or seen.add(a))]

    # Build friendly response plan
    agent_names = {"clean": "clean", "analyse": "analyse",
                   "visualise": "visualise", "automl": "train ML models",
                   "report": "write a report", "bias": "run a bias audit"}
    plan_parts = [agent_names.get(a, a) for a in agents]
    plan = f"I will {', '.join(plan_parts)} your dataset and teach you what each step means."

    return {
        "feasible":      True,
        "agents_to_run": agents,
        "target_col":    None,
        "decline_reason": None,
        "response_plan": plan,
        "teaching_focus": "data science pipeline"
    }
