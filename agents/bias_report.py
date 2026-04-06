# agents/bias_report.py — Bias Report Card Agent
# Goes beyond skewness — provides a comprehensive fairness audit

import pandas as pd
import numpy as np
from scipy import stats


def run_bias_audit(df: pd.DataFrame, target_col: str = None) -> dict:
    """
    Runs a comprehensive bias and fairness audit on the dataset.
    Returns a structured report with findings and recommendations.
    """
    report = {
        "skewness": {},
        "class_imbalance": None,
        "potential_proxies": [],
        "representation_gaps": [],
        "statistical_tests": [],
        "overall_risk": "Low",
        "recommendations": [],
        "grade": "A",
    }

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    # ── 1. Skewness analysis ───────────────────────────────────────────────
    for col in numeric_cols:
        skew = float(df[col].skew())
        report["skewness"][col] = {
            "value": round(skew, 3),
            "severity": "high" if abs(skew) > 2 else "moderate" if abs(skew) > 1 else "low",
            "direction": "right-skewed" if skew > 0 else "left-skewed" if skew < 0 else "symmetric"
        }

    high_skew = [c for c, v in report["skewness"].items() if v["severity"] == "high"]

    # ── 2. Class imbalance (if target specified) ───────────────────────────
    if target_col and target_col in df.columns:
        vc = df[target_col].value_counts(normalize=True)
        imbalance_ratio = float(vc.iloc[0] / vc.iloc[-1]) if len(vc) > 1 else 1.0
        majority_pct = float(vc.iloc[0] * 100)

        report["class_imbalance"] = {
            "target": target_col,
            "distribution": {str(k): round(float(v*100), 1) for k, v in vc.items()},
            "imbalance_ratio": round(imbalance_ratio, 2),
            "majority_class_pct": round(majority_pct, 1),
            "severity": "high" if imbalance_ratio > 10 else
                        "moderate" if imbalance_ratio > 3 else "low",
            "warning": imbalance_ratio > 3
        }

    # ── 3. Potential proxy variables ──────────────────────────────────────
    # Check columns with names that might encode protected characteristics
    protected_keywords = {
        "age": "Age discrimination risk",
        "gender": "Gender discrimination risk",
        "sex": "Gender discrimination risk",
        "race": "Racial discrimination risk",
        "ethnicity": "Racial discrimination risk",
        "nationality": "Nationality discrimination risk",
        "zip": "Geographic/socioeconomic proxy risk",
        "postcode": "Geographic/socioeconomic proxy risk",
        "income": "Socioeconomic proxy risk",
        "salary": "Socioeconomic proxy risk",
        "name": "Identity disclosure risk",
        "religion": "Religious discrimination risk",
        "disability": "Disability discrimination risk",
    }
    for col in df.columns:
        col_lower = col.lower()
        for keyword, risk in protected_keywords.items():
            if keyword in col_lower:
                report["potential_proxies"].append({
                    "column": col,
                    "risk": risk,
                    "recommendation": f"Evaluate whether '{col}' should be included in ML models"
                })

    # ── 4. Representation gaps in categorical columns ──────────────────────
    for col in cat_cols[:5]:
        vc = df[col].value_counts(normalize=True)
        if len(vc) > 1:
            max_pct = float(vc.iloc[0] * 100)
            min_pct = float(vc.iloc[-1] * 100)
            if min_pct < 5:
                report["representation_gaps"].append({
                    "column": col,
                    "dominant_value": str(vc.index[0]),
                    "dominant_pct": round(max_pct, 1),
                    "underrepresented_value": str(vc.index[-1]),
                    "underrepresented_pct": round(min_pct, 1),
                    "risk": "Underrepresented groups may be poorly modelled"
                })

    # ── 5. Statistical normality tests ────────────────────────────────────
    for col in numeric_cols[:5]:
        clean = df[col].dropna()
        if len(clean) >= 8:
            sample = clean.sample(min(5000, len(clean)), random_state=42)
            stat, p = stats.shapiro(sample) if len(sample) <= 5000 else (0, 0)
            report["statistical_tests"].append({
                "column": col,
                "test": "Shapiro-Wilk" if len(sample) <= 5000 else "Too large",
                "is_normal": bool(p > 0.05),
                "p_value": round(float(p), 4),
                "recommendation": "Normally distributed — parametric methods appropriate" if p > 0.05
                                  else "Non-normal — consider log transform or non-parametric methods"
            })

    # ── 6. Overall risk assessment ─────────────────────────────────────────
    risk_score = 0
    if len(high_skew) > 3: risk_score += 2
    elif len(high_skew) > 0: risk_score += 1
    if report["class_imbalance"] and report["class_imbalance"].get("severity") == "high": risk_score += 3
    elif report["class_imbalance"] and report["class_imbalance"].get("severity") == "moderate": risk_score += 1
    if len(report["potential_proxies"]) > 2: risk_score += 2
    elif len(report["potential_proxies"]) > 0: risk_score += 1
    if len(report["representation_gaps"]) > 1: risk_score += 1

    report["overall_risk"] = "High" if risk_score >= 5 else "Medium" if risk_score >= 2 else "Low"
    report["grade"] = "C" if risk_score >= 5 else "B" if risk_score >= 2 else "A"

    # ── 7. Recommendations ────────────────────────────────────────────────
    recs = []
    if high_skew:
        recs.append(f"Apply log transformation to highly skewed columns: {', '.join(high_skew[:3])}")
    if report["class_imbalance"] and report["class_imbalance"].get("warning"):
        recs.append("Address class imbalance using SMOTE oversampling or class_weight='balanced' in sklearn")
    if report["potential_proxies"]:
        recs.append("Review protected characteristic columns before deploying any model trained on this data")
    if report["representation_gaps"]:
        recs.append("Collect more data for underrepresented groups to improve model fairness")
    if not recs:
        recs.append("Dataset shows low bias risk. Continue with standard preprocessing.")
    recs.append("Always validate model performance separately across demographic groups (if available)")
    recs.append("Document all preprocessing decisions for audit trail compliance (EU AI Act)")
    report["recommendations"] = recs

    return report


def render_bias_report(st, report: dict) -> None:
    """Renders the bias report card in Streamlit."""
    TEAL = "#02C39A"; RED = "#EF4444"; AMBER = "#F59E0B"; GREEN = "#10B981"

    # Grade badge
    grade = report["grade"]
    risk = report["overall_risk"]
    grade_color = {"A": GREEN, "B": AMBER, "C": RED}.get(grade, TEAL)
    risk_color  = {"Low": GREEN, "Medium": AMBER, "High": RED}.get(risk, TEAL)

    st.markdown(f"""
    <div style="background:#161B22;border:2px solid {grade_color};border-radius:12px;
                padding:1.5rem;text-align:center;margin-bottom:1rem;">
        <div style="font-size:3rem;font-weight:900;color:{grade_color}">{grade}</div>
        <div style="color:#E6EDF3;font-size:1rem;">Bias Risk Grade</div>
        <div style="color:{risk_color};font-weight:bold;margin-top:.3rem">
            Overall Risk: {risk}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Skewness
    if report["skewness"]:
        st.markdown("#### Skewness Analysis")
        skew_data = [{"Column": c, "Skewness": v["value"],
                      "Severity": v["severity"].title(),
                      "Direction": v["direction"]}
                     for c, v in report["skewness"].items()]
        import pandas as pd
        st.dataframe(pd.DataFrame(skew_data), use_container_width=True, hide_index=True)

    # Class imbalance
    ci = report.get("class_imbalance")
    if ci:
        st.markdown("#### Class Imbalance")
        if ci["warning"]:
            st.warning(f"⚠️ **{ci['target']}** is imbalanced — ratio {ci['imbalance_ratio']}:1 "
                       f"(majority class: {ci['majority_class_pct']}%)")
        else:
            st.success(f"✅ **{ci['target']}** is reasonably balanced")
        st.write(ci["distribution"])

    # Proxy variables
    if report["potential_proxies"]:
        st.markdown("#### Potential Proxy Variables")
        for p in report["potential_proxies"]:
            st.warning(f"⚠️ **{p['column']}** — {p['risk']}")

    # Representation gaps
    if report["representation_gaps"]:
        st.markdown("#### Representation Gaps")
        for g in report["representation_gaps"]:
            st.error(f"🔴 **{g['column']}**: {g['underrepresented_value']} "
                     f"= only {g['underrepresented_pct']}% of data")

    # Recommendations
    st.markdown("#### Recommendations")
    for r in report["recommendations"]:
        st.markdown(f"- {r}")