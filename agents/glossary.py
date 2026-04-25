# agents/glossary.py
import streamlit as st
import json
import os
import random
from datetime import date

GLOSSARY_PROGRESS_FILE = "data/glossary_progress.json"

GLOSSARY = {
    "Mean": {"definition": "The arithmetic average — sum of all values divided by the count. Sensitive to outliers.", "category": "Statistics", "related": ["Median", "Mode", "Standard Deviation"], "example": "Mean income of [20k, 30k, 100k] = 50k — distorted by the high earner."},
    "Median": {"definition": "The middle value when data is sorted. Robust to outliers — preferred for skewed distributions.", "category": "Statistics", "related": ["Mean", "Skewness", "IQR"], "example": "Median income of [20k, 30k, 100k] = 30k — not affected by the high earner."},
    "Standard Deviation": {"definition": "Measures how spread out values are around the mean. Large std = high variability.", "category": "Statistics", "related": ["Mean", "Variance", "Normal Distribution"], "example": "Heights: mean=170cm, std=5cm means most people are 165-175cm."},
    "Correlation": {"definition": "Measures the strength and direction of a linear relationship between two variables. r ranges from -1 to +1.", "category": "Statistics", "related": ["Pearson Coefficient", "Causation", "Scatter Plot"], "example": "r = 0.9 between hours studied and exam score means strong positive relationship."},
    "Skewness": {"definition": "Measures the asymmetry of a distribution. Positive skew = long right tail. Negative skew = long left tail.", "category": "Statistics", "related": ["Normal Distribution", "Mean", "Median"], "example": "Income data is positively skewed — most earn average wages, few earn millions."},
    "P-value": {"definition": "The probability of observing results as extreme as the data, assuming the null hypothesis is true. p < 0.05 is typically significant.", "category": "Statistics", "related": ["Hypothesis Testing", "Null Hypothesis", "Confidence Interval"], "example": "p = 0.03 means there is a 3% chance the result occurred by random chance."},
    "Normal Distribution": {"definition": "A symmetric bell-shaped distribution where most values cluster around the mean.", "category": "Statistics", "related": ["Mean", "Standard Deviation", "Skewness"], "example": "Heights of adults approximately follow a normal distribution."},
    "IQR": {"definition": "Interquartile Range — the difference between Q3 and Q1. Used to detect outliers.", "category": "Statistics", "related": ["Quartile", "Outlier", "Box Plot"], "example": "Values outside Q1 - 1.5xIQR or Q3 + 1.5xIQR are flagged as outliers."},
    "Overfitting": {"definition": "When a model learns the training data too well including noise and fails to generalise to new data.", "category": "Machine Learning", "related": ["Underfitting", "Cross-Validation", "Regularisation"], "example": "A student who memorises exam answers but cannot apply knowledge to new questions."},
    "Underfitting": {"definition": "When a model is too simple to capture patterns in the data.", "category": "Machine Learning", "related": ["Overfitting", "Model Complexity", "Bias-Variance Tradeoff"], "example": "A linear model trying to fit a curved relationship will underfit."},
    "Cross-Validation": {"definition": "A technique to estimate model performance by splitting data into multiple train/test subsets and averaging results.", "category": "Machine Learning", "related": ["Train/Test Split", "Overfitting", "Generalisation"], "example": "5-fold CV splits data into 5 parts, trains on 4, tests on 1, repeated 5 times."},
    "Random Forest": {"definition": "An ensemble method that builds many decision trees and takes a majority vote.", "category": "Machine Learning", "related": ["Decision Tree", "Ensemble Learning", "Feature Importance"], "example": "Asking 100 experts and taking a majority vote instead of relying on one expert."},
    "Feature Importance": {"definition": "A score indicating how much each input column contributed to a model's predictions.", "category": "Machine Learning", "related": ["Random Forest", "Gradient Boosting", "Feature Selection"], "example": "Feature importance of 0.45 for age means age was the most influential predictor."},
    "Accuracy": {"definition": "The proportion of correct predictions out of all predictions. Misleading when classes are imbalanced.", "category": "Machine Learning", "related": ["Precision", "Recall", "F1 Score"], "example": "90% accuracy sounds good but if 90% of data is class A, always predicting A achieves this."},
    "EDA": {"definition": "Exploratory Data Analysis — the process of summarising and visualising data to discover patterns before modelling.", "category": "Data Science", "related": ["Data Cleaning", "Visualisation", "Statistics"], "example": "Plotting distributions, checking correlations, and identifying outliers before modelling."},
    "Data Cleaning": {"definition": "The process of detecting and fixing errors, missing values, duplicates, and inconsistencies in a dataset.", "category": "Data Science", "related": ["Missing Values", "Outlier", "Imputation"], "example": "Removing duplicate rows, filling missing ages with median, standardising column names."},
    "Missing Values": {"definition": "Cells with no data — represented as NaN, null, or blank. Must be handled before analysis or modelling.", "category": "Data Science", "related": ["Imputation", "Data Cleaning"], "example": "40 missing values in the age column — filled using median imputation."},
    "Outlier": {"definition": "A data point significantly different from other observations. Detected using IQR or Z-score methods.", "category": "Data Science", "related": ["IQR", "Z-Score", "Box Plot"], "example": "An income of 2,000,000 in a dataset of typical salaries is an outlier."},
    "Histogram": {"definition": "A bar chart showing the frequency distribution of a numeric variable, divided into bins.", "category": "Visualisation", "related": ["Distribution", "Bins", "Skewness"], "example": "A histogram of ages shows most customers are between 25 and 45."},
    "Box Plot": {"definition": "A chart showing median, quartiles, and outliers for a numeric variable.", "category": "Visualisation", "related": ["IQR", "Outlier", "Median"], "example": "The box covers Q1 to Q3, the line is median, dots beyond whiskers are outliers."},
    "Heatmap": {"definition": "A colour-coded matrix showing values — commonly used to visualise correlation matrices.", "category": "Visualisation", "related": ["Correlation", "Matrix"], "example": "Dark green cells in a correlation heatmap indicate strong positive correlations."},
    "Bias": {"definition": "Systematic error in a dataset or model that produces unfair or inaccurate outcomes for certain groups.", "category": "Ethics", "related": ["Fairness", "Proxy Variable", "Class Imbalance"], "example": "A hiring model trained on historical data may disadvantage women if underrepresented."},
    "Fairness": {"definition": "The principle that AI systems should treat all individuals and groups equitably without discrimination.", "category": "Ethics", "related": ["Bias", "EU AI Act", "Protected Characteristics"], "example": "A loan model should not reject applications based on postcode as a proxy for race."},
    "EU AI Act": {"definition": "European regulation (2024) requiring AI systems to be transparent, explainable, and free from discriminatory bias.", "category": "Ethics", "related": ["Bias", "Fairness", "Explainability"], "example": "A hospital using AI for diagnosis must document bias checks and provide explanations."},
    "Pandas": {"definition": "A Python library for data manipulation and analysis — provides DataFrame structures for tabular data.", "category": "Tools", "related": ["NumPy", "DataFrame", "Python"], "example": "df.dropna() removes rows with missing values."},
    "Streamlit": {"definition": "A Python framework for building and deploying interactive web applications for data science.", "category": "Tools", "related": ["Python", "Plotly", "Deployment"], "example": "DataForge is built entirely with Streamlit."},
    "LangChain": {"definition": "A framework for building applications powered by large language models.", "category": "Tools", "related": ["GPT-4", "Multi-Agent", "Orchestrator"], "example": "DataForge uses LangChain to coordinate its pipeline agents."},
    "Plotly": {"definition": "A Python library for creating interactive charts.", "category": "Tools", "related": ["Matplotlib", "Seaborn", "Visualisation"], "example": "DataForge uses Plotly so students can hover over data points for details."},
    "scikit-learn": {"definition": "The most widely used Python machine learning library.", "category": "Tools", "related": ["Python", "Machine Learning", "Pandas"], "example": "DataForge AutoML agent uses scikit-learn to train and compare algorithms."},
}


def get_term_of_the_day():
    terms = list(GLOSSARY.keys())
    idx   = hash(str(date.today())) % len(terms)
    term  = terms[idx]
    return term, GLOSSARY[term]


def get_categories():
    return sorted(set(v["category"] for v in GLOSSARY.values()))


def _load_glossary_progress():
    os.makedirs("data", exist_ok=True)
    if os.path.exists(GLOSSARY_PROGRESS_FILE):
        with open(GLOSSARY_PROGRESS_FILE) as f:
            return json.load(f)
    return {}


def _save_glossary_progress(progress):
    os.makedirs("data", exist_ok=True)
    with open(GLOSSARY_PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)


def set_term_status(username, term, status):
    progress = _load_glossary_progress()
    if username not in progress:
        progress[username] = {}
    progress[username][term] = status
    _save_glossary_progress(progress)


def get_term_statuses(username):
    progress = _load_glossary_progress()
    return progress.get(username, {})


def ai_define_term(client, term):
    if not client:
        return f"**{term}**: Add your OpenAI API key for AI-powered definitions."
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "system",
                "content": "You are a data science educator. Define the term in 2-3 sentences with one example. Format: Definition: ... | Example: ... | Related: term1, term2"
            }, {
                "role": "user",
                "content": f"Define: {term}"
            }],
            max_tokens=200, temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Could not generate definition: {e}"


def render_glossary_tab(username="", gpt_client=None):
    st.markdown("### 📖 Data Science Glossary")
    st.markdown("Your A-Z reference for data science, machine learning, statistics and AI ethics.")

    term_name, term_data = get_term_of_the_day()
    st.markdown(
        f'<div style="background:linear-gradient(135deg,#028090,#02C39A);'
        f'border-radius:12px;padding:1.2rem 1.5rem;margin-bottom:1rem">'
        f'<div style="color:white;font-size:.8rem;font-weight:bold;text-transform:uppercase">✨ Term of the Day</div>'
        f'<div style="color:white;font-size:1.4rem;font-weight:900;margin:.3rem 0">{term_name}</div>'
        f'<div style="color:rgba(255,255,255,.9);font-size:.95rem">{term_data["definition"]}</div>'
        f'<div style="color:rgba(255,255,255,.7);font-size:.82rem;margin-top:.5rem">Category: {term_data["category"]}</div>'
        f'</div>', unsafe_allow_html=True)

    st.divider()

    col_s, col_c = st.columns([3, 2])
    with col_s:
        search = st.text_input("Search terms", placeholder="e.g. correlation, overfitting...",
                                key="glossary_search", label_visibility="collapsed")
    with col_c:
        categories = ["All"] + get_categories()
        cat_filter = st.selectbox("Filter by category", categories,
                                   key="glossary_cat", label_visibility="collapsed")

    statuses = get_term_statuses(username) if username else {}

    filtered = {}
    for term, data in sorted(GLOSSARY.items()):
        if search and search.lower() not in term.lower() and search.lower() not in data["definition"].lower():
            continue
        if cat_filter != "All" and data["category"] != cat_filter:
            continue
        filtered[term] = data

    st.markdown(f"**{len(filtered)} term(s)** | "
                f"✅ {sum(1 for s in statuses.values() if s=='know')} known · "
                f"📚 {sum(1 for s in statuses.values() if s=='learning')} learning")
    st.divider()

    for term, data in filtered.items():
        term_status = statuses.get(term, "unmarked")
        status_icon = "✅" if term_status == "know" else "📚" if term_status == "learning" else "○"

        with st.expander(f"{status_icon} **{term}** — *{data['category']}*"):
            st.markdown(f"**Definition:** {data['definition']}")
            if data.get("example"):
                st.markdown(
                    f'<div style="background:#0D2137;border-left:3px solid #028090;'
                    f'padding:.5rem 1rem;border-radius:0 6px 6px 0;'
                    f'font-size:.9rem;color:#94A3B8;margin:.5rem 0">'
                    f'📌 <em>{data["example"]}</em></div>', unsafe_allow_html=True)
            if data.get("related"):
                st.markdown("**Related:** " + " · ".join(f"`{r}`" for r in data["related"]))

            if username:
                b1, b2 = st.columns(2)
                with b1:
                    if st.button("✅ I Know This", key=f"know_{term}"):
                        set_term_status(username, term,
                                         "unmarked" if term_status == "know" else "know")
                        st.rerun()
                with b2:
                    if st.button("📚 Still Learning", key=f"learning_{term}"):
                        set_term_status(username, term,
                                         "unmarked" if term_status == "learning" else "learning")
                        st.rerun()

    st.divider()
    st.markdown("### 🤖 AI Definition Lookup")
    st.markdown("Can't find a term? Ask the AI for an instant definition.")
    col_ai1, col_ai2 = st.columns([4, 1])
    with col_ai1:
        custom_term = st.text_input("Enter any data science term:",
                                     placeholder="e.g. SHAP values, t-SNE, SMOTE...",
                                     key="ai_lookup_term", label_visibility="collapsed")
    with col_ai2:
        lookup_btn = st.button("Define", key="ai_define_btn", use_container_width=True)

    if lookup_btn and custom_term.strip():
        if custom_term.strip() in GLOSSARY:
            st.info(f"**{custom_term}** is already in the glossary above!")
        else:
            with st.spinner(f"GPT-4 is defining '{custom_term}'..."):
                definition = ai_define_term(gpt_client, custom_term.strip())
            st.markdown(
                f'<div style="background:#161B22;border-left:4px solid #02C39A;'
                f'padding:1rem 1.4rem;border-radius:0 8px 8px 0;color:#E6EDF3">'
                f'<strong>{custom_term}</strong><br><br>{definition}</div>',
                unsafe_allow_html=True)
