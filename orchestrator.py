# orchestrator.py
# LangChain Orchestrator — coordinates all DataForge agents

import pandas as pd
import os
from dotenv import load_dotenv

from agents.cleaner import clean_data
from agents.analyser import analyse_data
from agents.visualiser import generate_charts
from agents.reporter import generate_report, generate_report_fallback

load_dotenv()


def run_pipeline(df: pd.DataFrame, use_gpt: bool = False, progress_callback=None) -> dict:
    """
    Master orchestrator. Runs all 4 agents in sequence.
    Returns a results dict with everything needed for the UI.

    Args:
        df: Raw uploaded dataframe
        use_gpt: Whether to use OpenAI GPT-4 for the report
        progress_callback: Optional callable(step: int, message: str)

    Returns:
        {
            "cleaned_df": pd.DataFrame,
            "audit_log": list[str],
            "insights": dict,
            "charts": list[dict],
            "report": str,
            "success": bool,
            "error": str | None
        }
    """

    def update(step, msg):
        if progress_callback:
            progress_callback(step, msg)

    results = {
        "cleaned_df": None,
        "audit_log": [],
        "insights": {},
        "charts": [],
        "report": "",
        "success": False,
        "error": None,
    }

    try:
        # ── STEP 1: Clean ────────────────────────────────────────────────────
        update(1, "🧹 Agent 1: Cleaning and validating data...")
        cleaned_df, audit_log = clean_data(df.copy())
        results["cleaned_df"] = cleaned_df
        results["audit_log"] = audit_log

        # ── STEP 2: Analyse ──────────────────────────────────────────────────
        update(2, "📊 Agent 2: Running statistical analysis...")
        insights = analyse_data(cleaned_df)
        results["insights"] = insights

        # ── STEP 3: Visualise ────────────────────────────────────────────────
        update(3, "📈 Agent 3: Generating charts and visualisations...")
        charts = generate_charts(cleaned_df, insights)
        results["charts"] = charts

        # ── STEP 4: Report ───────────────────────────────────────────────────
        update(4, "✍️ Agent 4: Writing analysis report...")
        api_key = os.getenv("OPENAI_API_KEY", "")

        if use_gpt and api_key and api_key != "your_openai_api_key_here":
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            report = generate_report(insights, audit_log, client)
            update(4, "✍️ Agent 4: GPT-4 report written.")
        else:
            report = generate_report_fallback(insights, audit_log)
            update(4, "✍️ Agent 4: Report written (fallback mode — no API key needed).")

        results["report"] = report
        results["success"] = True
        update(5, "✅ Pipeline complete!")

    except Exception as e:
        results["error"] = str(e)
        results["success"] = False

    return results