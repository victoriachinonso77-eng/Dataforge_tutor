# agents/chat_orchestrator.py
# Conversational orchestrator — runs only the agents the user asked for

import time
import pandas as pd


def run_selected_agents(df_raw, agents_to_run, target_col=None,
                         use_gpt=False, gpt_client=None,
                         df2=None, progress_callback=None):
    results = {
        "success":     True,
        "error":       None,
        "agents_ran":  [],
        "cleaned_df":  None,
        "audit_log":   [],
        "insights":    {},
        "charts":      [],
        "report":      None,
        "ml_results":  None,
        "bias_report": None,
        "comparison":  None,
        "elapsed":     0,
    }

    start      = time.time()
    step       = 0
    total      = len(agents_to_run)
    working_df = df_raw.copy()

    def progress(msg):
        nonlocal step
        step += 1
        if progress_callback:
            progress_callback(step, total, msg)

    try:
        # ── Agent 1: Cleaner ──────────────────────────────────────────
        if "clean" in agents_to_run:
            progress("Cleaning your data...")
            try:
                # Try different function names — handles different versions
                from agents.cleaner import clean_dataframe
                working_df, audit_log = clean_dataframe(working_df)
            except ImportError:
                try:
                    from agents.cleaner import run_cleaning
                    result = run_cleaning(working_df)
                    working_df = result.get("cleaned_df", working_df)
                    audit_log  = result.get("audit_log", [])
                except ImportError:
                    try:
                        from orchestrator import run_pipeline
                        pipe_result = run_pipeline(working_df, use_gpt=False)
                        working_df  = pipe_result.get("cleaned_df", working_df)
                        audit_log   = pipe_result.get("audit_log", [])
                    except Exception:
                        audit_log = ["Data passed through — cleaning function not found"]
            results["cleaned_df"] = working_df
            results["audit_log"]  = audit_log
            results["agents_ran"].append("clean")
        else:
            results["cleaned_df"] = working_df
            results["audit_log"]  = ["Data passed through without cleaning."]

        df = results["cleaned_df"]

        # ── Agent 2: Analyser ─────────────────────────────────────────
        if "analyse" in agents_to_run:
            progress("Analysing your data...")
            try:
                from agents.analyser import analyse_dataframe
                insights = analyse_dataframe(df)
            except Exception:
                try:
                    from agents.analyser import run_analysis
                    insights = run_analysis(df)
                except Exception as e:
                    insights = {}
                    print(f"Analyser error: {e}")
            results["insights"] = insights
            results["agents_ran"].append("analyse")

        # ── Agent 3: Visualiser ───────────────────────────────────────
        if "visualise" in agents_to_run:
            progress("Creating visualisations...")
            try:
                from agents.visualiser_plotly import generate_plotly_charts
                charts = generate_plotly_charts(df, results.get("insights", {}))
                results["charts"] = charts
                results["agents_ran"].append("visualise")
            except Exception as e:
                print(f"Visualiser error: {e}")

        # ── Agent 4: AutoML ───────────────────────────────────────────
        if "automl" in agents_to_run and target_col:
            progress(f"Training ML models to predict {target_col}...")
            try:
                from agents.automl import run_automl
                ml_res = run_automl(df, target_col)
                results["ml_results"] = ml_res
                results["agents_ran"].append("automl")
            except Exception as e:
                print(f"AutoML error: {e}")

        # ── Agent 5: Reporter ─────────────────────────────────────────
        if "report" in agents_to_run:
            progress("Writing your analysis report...")
            try:
                from agents.reporter import generate_report
                report = generate_report(df, results.get("insights", {}),
                                          results.get("audit_log", []),
                                          use_gpt=use_gpt, client=gpt_client)
                results["report"] = report
                results["agents_ran"].append("report")
            except Exception as e:
                print(f"Reporter error: {e}")

        # ── Agent 6: Bias Report ──────────────────────────────────────
        if "bias" in agents_to_run:
            progress("Running bias audit...")
            try:
                from agents.bias_report import run_bias_audit
                bias = run_bias_audit(df)
                results["bias_report"] = bias
                results["agents_ran"].append("bias")
            except Exception as e:
                print(f"Bias error: {e}")

        # ── Agent 7: Compare ──────────────────────────────────────────
        if "compare" in agents_to_run and df2 is not None:
            progress("Comparing datasets...")
            try:
                from agents.multi_dataset import compare_datasets
                results["comparison"] = compare_datasets(df, df2)
                results["agents_ran"].append("compare")
            except Exception as e:
                print(f"Compare error: {e}")

    except Exception as e:
        results["success"] = False
        results["error"]   = str(e)

    results["elapsed"] = round(time.time() - start, 2)
    return results
