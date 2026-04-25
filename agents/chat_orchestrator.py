# agents/chat_orchestrator.py
# Conversational orchestrator — runs only the agents the user asked for
# Returns structured results for each agent that ran

import time
import pandas as pd


def run_selected_agents(df_raw: pd.DataFrame, agents_to_run: list,
                         target_col: str = None, use_gpt: bool = False,
                         gpt_client=None, df2: pd.DataFrame = None,
                         progress_callback=None) -> dict:
    """
    Runs only the agents requested by the user via chat.
    Returns a results dict with outputs from each agent that ran.
    """
    results = {
        "success":       True,
        "error":         None,
        "agents_ran":    [],
        "cleaned_df":    None,
        "audit_log":     [],
        "insights":      {},
        "charts":        [],
        "report":        None,
        "ml_results":    None,
        "bias_report":   None,
        "comparison":    None,
        "elapsed":       0,
    }

    start = time.time()
    step  = 0
    total = len(agents_to_run)

    def progress(msg):
        nonlocal step
        step += 1
        if progress_callback:
            progress_callback(step, total, msg)

    working_df = df_raw.copy()

    try:
        # ── Agent 1: Cleaner ─────────────────────────────────────────────
        if "clean" in agents_to_run:
            progress("Cleaning your data...")
            from agents.cleaner import clean_dataframe
            working_df, audit_log = clean_dataframe(working_df)
            results["cleaned_df"] = working_df
            results["audit_log"]  = audit_log
            results["agents_ran"].append("clean")

        else:
            # Pass raw data through even if cleaning not requested
            results["cleaned_df"] = working_df
            results["audit_log"]  = ["Data passed through without cleaning as per your request."]

        df = results["cleaned_df"]

        # ── Agent 2: Analyser ────────────────────────────────────────────
        if "analyse" in agents_to_run:
            progress("Analysing your data...")
            from agents.analyser import analyse_dataframe
            insights = analyse_dataframe(df)
            results["insights"] = insights
            results["agents_ran"].append("analyse")

        # ── Agent 3: Visualiser ──────────────────────────────────────────
        if "visualise" in agents_to_run:
            progress("Creating visualisations...")
            from agents.visualiser_plotly import generate_plotly_charts
            insights_for_charts = results.get("insights", {})
            charts = generate_plotly_charts(df, insights_for_charts)
            results["charts"] = charts
            results["agents_ran"].append("visualise")

        # ── Agent 4: AutoML ──────────────────────────────────────────────
        if "automl" in agents_to_run and target_col:
            progress(f"Training ML models to predict {target_col}...")
            from agents.automl import run_automl
            ml_res = run_automl(df, target_col)
            results["ml_results"] = ml_res
            results["agents_ran"].append("automl")

        # ── Agent 5: Reporter ────────────────────────────────────────────
        if "report" in agents_to_run:
            progress("Writing your analysis report...")
            from agents.reporter import generate_report
            insights_for_report = results.get("insights", {})
            audit   = results.get("audit_log", [])
            report  = generate_report(df, insights_for_report, audit,
                                       use_gpt=use_gpt, client=gpt_client)
            results["report"] = report
            results["agents_ran"].append("report")

        # ── Agent 6: Bias Report ─────────────────────────────────────────
        if "bias" in agents_to_run:
            progress("Running bias and fairness audit...")
            from agents.bias_report import run_bias_audit
            bias = run_bias_audit(df)
            results["bias_report"] = bias
            results["agents_ran"].append("bias")

        # ── Agent 7: Compare ─────────────────────────────────────────────
        if "compare" in agents_to_run and df2 is not None:
            progress("Comparing your two datasets...")
            from agents.multi_dataset import compare_datasets
            comparison = compare_datasets(df, df2)
            results["comparison"] = comparison
            results["agents_ran"].append("compare")

    except Exception as e:
        results["success"] = False
        results["error"]   = str(e)

    results["elapsed"] = round(time.time() - start, 2)
    return results