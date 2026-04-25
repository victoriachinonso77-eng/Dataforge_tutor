# agents/glossary.py — Upgraded Data Science Glossary Tab

import streamlit as st
import random
import json
import os
from datetime import date

GLOSSARY = {
    "A": [
        {"term": "Accuracy", "definition": "The proportion of correct predictions made by a model out of all predictions. Calculated as (TP + TN) / Total. Can be misleading on imbalanced datasets.", "category": "Evaluation", "related": ["Precision", "Recall", "F1 Score"]},
        {"term": "Algorithm", "definition": "A step-by-step procedure or set of rules that a computer follows to solve a problem or complete a task, such as training a machine learning model.", "category": "Core Concepts", "related": ["Model", "Machine Learning (ML)"]},
        {"term": "Anomaly Detection", "definition": "The process of identifying unusual patterns or outliers in data that do not conform to expected behaviour. Used in fraud detection and network security.", "category": "ML Techniques", "related": ["Outlier", "Clustering"]},
        {"term": "AutoML", "definition": "Automated Machine Learning — the process of automating the selection, composition, and parameterisation of machine learning models with minimal human intervention.", "category": "ML Techniques", "related": ["Hyperparameter", "Model"]},
    ],
    "B": [
        {"term": "Bagging", "definition": "An ensemble technique that trains multiple models on random subsets of the training data and combines their predictions to reduce variance and overfitting.", "category": "ML Techniques", "related": ["Random Forest", "Ensemble Learning", "Overfitting"]},
        {"term": "Bias", "definition": "In ML, bias refers to errors from overly simplistic assumptions. High bias causes underfitting. In data, bias refers to systematic errors that skew results unfairly.", "category": "Core Concepts", "related": ["Variance", "Underfitting", "Overfitting"]},
        {"term": "Boosting", "definition": "An ensemble method that trains models sequentially, where each model focuses on correcting the errors of the previous one. Examples include XGBoost and AdaBoost.", "category": "ML Techniques", "related": ["Bagging", "Ensemble Learning", "XGBoost"]},
    ],
    "C": [
        {"term": "Classification", "definition": "A supervised learning task where the model predicts which category an input belongs to, such as spam or not spam, or dog or cat.", "category": "ML Techniques", "related": ["Regression", "Supervised Learning", "Label"]},
        {"term": "Clustering", "definition": "An unsupervised learning technique that groups similar data points together without predefined labels. Examples include K-Means and DBSCAN.", "category": "ML Techniques", "related": ["K-Means", "Unsupervised Learning"]},
        {"term": "Confusion Matrix", "definition": "A table showing the performance of a classification model by comparing predicted labels against actual labels across True Positives, False Positives, True Negatives, and False Negatives.", "category": "Evaluation", "related": ["Accuracy", "Precision", "Recall"]},
        {"term": "Cross-Validation", "definition": "A technique for evaluating a model by splitting data into multiple folds, training on some and testing on others, to get a more reliable estimate of performance.", "category": "Evaluation", "related": ["Overfitting", "Train/Test Split"]},
        {"term": "Correlation", "definition": "A statistical measure of how strongly two variables are related. Ranges from -1 (perfect negative) to +1 (perfect positive). Does not imply causation.", "category": "Statistics", "related": ["Multicollinearity", "Feature Selection"]},
    ],
    "D": [
        {"term": "Data Cleaning", "definition": "The process of detecting and correcting errors, inconsistencies, and missing values in a dataset to improve its quality before analysis or modelling.", "category": "Data Processing", "related": ["Missing Values", "Outlier", "Null Value"]},
        {"term": "Data Leakage", "definition": "When information from outside the training dataset is used to create the model, leading to overly optimistic performance that does not generalise to new data.", "category": "Core Concepts", "related": ["Overfitting", "Train/Test Split"]},
        {"term": "Decision Tree", "definition": "A model that splits data into branches based on feature values, making decisions at each node until reaching a prediction at the leaf nodes.", "category": "ML Techniques", "related": ["Random Forest", "Overfitting"]},
        {"term": "Dimensionality Reduction", "definition": "Techniques that reduce the number of features in a dataset while preserving important information. PCA is a common example.", "category": "Data Processing", "related": ["Principal Component Analysis (PCA)", "Feature Selection"]},
    ],
    "E": [
        {"term": "Ensemble Learning", "definition": "Combining multiple machine learning models to produce better predictions than any single model alone. Bagging and Boosting are two main approaches.", "category": "ML Techniques", "related": ["Bagging", "Boosting", "Random Forest"]},
        {"term": "Epoch", "definition": "One complete pass through the entire training dataset during the training of a neural network or deep learning model.", "category": "Deep Learning", "related": ["Neural Network", "Gradient Descent"]},
        {"term": "Exploratory Data Analysis (EDA)", "definition": "The initial step of analysing a dataset to summarise its main characteristics, often using visualisations, before applying machine learning models.", "category": "Data Processing", "related": ["Visualisation", "Statistics"]},
    ],
    "F": [
        {"term": "F1 Score", "definition": "The harmonic mean of Precision and Recall. A balanced metric useful when class distribution is uneven. Ranges from 0 (worst) to 1 (best).", "category": "Evaluation", "related": ["Precision", "Recall", "Accuracy"]},
        {"term": "Feature", "definition": "An individual measurable property or characteristic of the data used as input to a machine learning model, also called a variable or column.", "category": "Core Concepts", "related": ["Feature Engineering", "Target Variable"]},
        {"term": "Feature Engineering", "definition": "The process of using domain knowledge to create, transform, or select features that improve a machine learning model's performance.", "category": "Data Processing", "related": ["Feature", "Feature Selection"]},
        {"term": "Feature Selection", "definition": "Choosing the most relevant features from a dataset to use in a model, removing redundant or irrelevant ones to improve performance and reduce complexity.", "category": "Data Processing", "related": ["Feature Engineering", "Dimensionality Reduction"]},
    ],
    "G": [
        {"term": "Gradient Descent", "definition": "An optimisation algorithm that iteratively adjusts model parameters in the direction that minimises the loss function, like rolling a ball downhill.", "category": "Deep Learning", "related": ["Loss Function", "Neural Network", "Epoch"]},
    ],
    "H": [
        {"term": "Hyperparameter", "definition": "A parameter set before training a model that controls the learning process, such as learning rate or number of trees. Different from parameters learned during training.", "category": "ML Techniques", "related": ["Model", "Cross-Validation", "AutoML"]},
    ],
    "I": [
        {"term": "Imputation", "definition": "The process of replacing missing values in a dataset with substituted values such as the mean, median, or a predicted value.", "category": "Data Processing", "related": ["Missing Values", "Data Cleaning"]},
        {"term": "Imbalanced Dataset", "definition": "A dataset where one class is significantly more frequent than others, which can cause a model to be biased towards the majority class.", "category": "Core Concepts", "related": ["Accuracy", "F1 Score", "Recall"]},
    ],
    "K": [
        {"term": "K-Means", "definition": "A clustering algorithm that partitions data into K groups by minimising the distance between data points and their cluster centre (centroid).", "category": "ML Techniques", "related": ["Clustering", "Unsupervised Learning"]},
        {"term": "K-Nearest Neighbours (KNN)", "definition": "A classification algorithm that assigns a label to a data point based on the majority label of its K nearest neighbours in the feature space.", "category": "ML Techniques", "related": ["Classification", "Supervised Learning"]},
        {"term": "Kaggle", "definition": "An online platform for data science competitions and datasets, widely used for learning and practising machine learning with real-world data.", "category": "Tools", "related": []},
    ],
    "L": [
        {"term": "Label", "definition": "The target output value in a supervised learning dataset — what the model is trying to predict, such as 'spam' or 'not spam'.", "category": "Core Concepts", "related": ["Classification", "Supervised Learning", "Target Variable"]},
        {"term": "Linear Regression", "definition": "A model that predicts a continuous numeric output by fitting a straight line through the data, minimising the sum of squared errors.", "category": "ML Techniques", "related": ["Regression", "Loss Function"]},
        {"term": "Logistic Regression", "definition": "Despite the name, a classification algorithm that predicts the probability of a binary outcome using a sigmoid function.", "category": "ML Techniques", "related": ["Classification", "Linear Regression"]},
        {"term": "Loss Function", "definition": "A function that measures how far a model's predictions are from the true values. The model is trained by minimising this function.", "category": "Core Concepts", "related": ["Gradient Descent", "Overfitting"]},
    ],
    "M": [
        {"term": "Machine Learning (ML)", "definition": "A branch of AI where systems learn patterns from data and improve their performance on tasks without being explicitly programmed.", "category": "Core Concepts", "related": ["Algorithm", "Model"]},
        {"term": "Mean", "definition": "The average of a set of values, calculated by summing all values and dividing by the count. Sensitive to outliers.", "category": "Statistics", "related": ["Median", "Standard Deviation"]},
        {"term": "Median", "definition": "The middle value of a sorted dataset. More robust to outliers than the mean and better represents the centre of skewed data.", "category": "Statistics", "related": ["Mean", "Skewness"]},
        {"term": "Missing Values", "definition": "Data points that are absent from a dataset, represented as NaN or null. Must be handled before modelling, typically by removal or imputation.", "category": "Data Processing", "related": ["Imputation", "Data Cleaning", "Null Value"]},
        {"term": "Model", "definition": "A mathematical representation of a pattern in data, trained on examples and used to make predictions or decisions on new, unseen data.", "category": "Core Concepts", "related": ["Algorithm", "Machine Learning (ML)"]},
        {"term": "Multicollinearity", "definition": "When two or more features in a dataset are highly correlated with each other, which can make it difficult to determine their individual effects on the target.", "category": "Statistics", "related": ["Correlation", "Feature Selection"]},
    ],
    "N": [
        {"term": "Naive Bayes", "definition": "A probabilistic classifier based on Bayes' theorem that assumes all features are independent of each other. Fast and effective for text classification.", "category": "ML Techniques", "related": ["Classification"]},
        {"term": "Neural Network", "definition": "A computing system loosely inspired by the human brain, consisting of layers of interconnected nodes that learn patterns from data through training.", "category": "Deep Learning", "related": ["Epoch", "Gradient Descent"]},
        {"term": "Normalisation", "definition": "Scaling numerical features to a standard range (usually 0 to 1) so that no single feature dominates due to its scale.", "category": "Data Processing", "related": ["Standardisation", "Feature Engineering"]},
        {"term": "Null Value", "definition": "A missing or undefined value in a dataset, often represented as NaN (Not a Number) in Python's Pandas library.", "category": "Data Processing", "related": ["Missing Values", "Imputation"]},
    ],
    "O": [
        {"term": "Outlier", "definition": "A data point that lies far from the rest of the data. Outliers can indicate errors in data collection or genuinely unusual observations.", "category": "Statistics", "related": ["Anomaly Detection", "Data Cleaning"]},
        {"term": "Overfitting", "definition": "When a model learns the training data too well, including its noise, and performs poorly on new unseen data. Prevented by regularisation and cross-validation.", "category": "Core Concepts", "related": ["Underfitting", "Bias", "Cross-Validation"]},
    ],
    "P": [
        {"term": "Pandas", "definition": "A Python library for data manipulation and analysis, providing DataFrame and Series structures for working with tabular and time series data.", "category": "Tools", "related": ["Scikit-learn"]},
        {"term": "Precision", "definition": "The proportion of positive predictions that were actually correct. Calculated as TP / (TP + FP). Important when false positives are costly.", "category": "Evaluation", "related": ["Recall", "F1 Score", "Confusion Matrix"]},
        {"term": "Principal Component Analysis (PCA)", "definition": "A dimensionality reduction technique that transforms features into a smaller set of uncorrelated components that capture the most variance in the data.", "category": "ML Techniques", "related": ["Dimensionality Reduction", "Feature Selection"]},
        {"term": "Proxy Variable", "definition": "A variable correlated with a protected attribute such as race or gender that can introduce bias into a model even when the protected attribute is excluded.", "category": "Ethics", "related": ["Bias", "Feature"]},
    ],
    "R": [
        {"term": "Random Forest", "definition": "An ensemble model that builds many decision trees on random subsets of data and features, then combines their predictions by voting or averaging.", "category": "ML Techniques", "related": ["Decision Tree", "Bagging", "Ensemble Learning"]},
        {"term": "Recall", "definition": "The proportion of actual positives that were correctly identified by the model. Calculated as TP / (TP + FN). Important when false negatives are costly.", "category": "Evaluation", "related": ["Precision", "F1 Score", "Confusion Matrix"]},
        {"term": "Regression", "definition": "A supervised learning task where the model predicts a continuous numeric output, such as predicting house prices or temperature.", "category": "ML Techniques", "related": ["Classification", "Linear Regression"]},
        {"term": "ROC-AUC", "definition": "Receiver Operating Characteristic — Area Under Curve. A metric measuring a model's ability to distinguish between classes across all classification thresholds.", "category": "Evaluation", "related": ["Precision", "Recall", "Accuracy"]},
    ],
    "S": [
        {"term": "Scikit-learn", "definition": "A Python machine learning library providing tools for classification, regression, clustering, and preprocessing, built on NumPy and SciPy.", "category": "Tools", "related": ["Pandas", "Model"]},
        {"term": "Skewness", "definition": "A measure of the asymmetry of a data distribution. Positive skew means a long right tail; negative skew means a long left tail.", "category": "Statistics", "related": ["Mean", "Median", "Outlier"]},
        {"term": "Standard Deviation", "definition": "A measure of how spread out values are around the mean. A high standard deviation means values are widely dispersed.", "category": "Statistics", "related": ["Mean", "Variance"]},
        {"term": "Standardisation", "definition": "Scaling features so they have a mean of 0 and standard deviation of 1. Makes features comparable regardless of their original units.", "category": "Data Processing", "related": ["Normalisation", "Feature Engineering"]},
        {"term": "Supervised Learning", "definition": "A type of machine learning where the model is trained on labelled data — each input has a known correct output the model learns to predict.", "category": "Core Concepts", "related": ["Unsupervised Learning", "Classification", "Regression"]},
        {"term": "Support Vector Machine (SVM)", "definition": "A classification algorithm that finds the optimal boundary that best separates classes in the feature space with the maximum margin.", "category": "ML Techniques", "related": ["Classification"]},
    ],
    "T": [
        {"term": "Target Variable", "definition": "The output variable that a machine learning model is trained to predict. Also called the dependent variable, label, or response variable.", "category": "Core Concepts", "related": ["Feature", "Label", "Supervised Learning"]},
        {"term": "Train/Test Split", "definition": "Dividing a dataset into a training set used to train the model and a test set used to evaluate it on unseen data.", "category": "Evaluation", "related": ["Cross-Validation", "Overfitting"]},
        {"term": "Transfer Learning", "definition": "Using a model pre-trained on one task as the starting point for a model on a different but related task. Common in deep learning and NLP.", "category": "Deep Learning", "related": ["Neural Network"]},
    ],
    "U": [
        {"term": "Underfitting", "definition": "When a model is too simple to capture the underlying patterns in the data, resulting in poor performance on both training and test data.", "category": "Core Concepts", "related": ["Overfitting", "Bias"]},
        {"term": "Unsupervised Learning", "definition": "A type of machine learning where the model is trained on unlabelled data and must find patterns or structure on its own.", "category": "Core Concepts", "related": ["Supervised Learning", "Clustering"]},
    ],
    "V": [
        {"term": "Variance", "definition": "A measure of how much a model's predictions fluctuate for different training datasets. High variance causes overfitting.", "category": "Core Concepts", "related": ["Bias", "Overfitting", "Standard Deviation"]},
        {"term": "Visualisation", "definition": "The representation of data through charts, graphs, and plots to help identify patterns, trends, and outliers that are not obvious in raw numbers.", "category": "Data Processing", "related": ["Exploratory Data Analysis (EDA)"]},
    ],
    "W": [
        {"term": "Weight", "definition": "A learnable parameter in a machine learning model that is adjusted during training to minimise the loss function.", "category": "Deep Learning", "related": ["Neural Network", "Gradient Descent", "Loss Function"]},
    ],
    "X": [
        {"term": "XGBoost", "definition": "An optimised gradient boosting algorithm known for its speed and performance. Widely used in data science competitions and industry.", "category": "ML Techniques", "related": ["Boosting", "Ensemble Learning", "Random Forest"]},
    ],
}

CATEGORIES = sorted(set(entry["category"] for terms in GLOSSARY.values() for entry in terms))
PROGRESS_FILE = "data/glossary_progress.json"


# ── PROGRESS HELPERS ──

def _load_progress() -> dict:
    if not os.path.exists(PROGRESS_FILE):
        return {}
    try:
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_progress(data: dict) -> None:
    os.makedirs("data", exist_ok=True)
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _get_user_progress(username: str) -> dict:
    return _load_progress().get(username, {})


def _set_term_status(username: str, term: str, status: str) -> None:
    all_progress = _load_progress()
    if username not in all_progress:
        all_progress[username] = {}
    all_progress[username][term] = status
    _save_progress(all_progress)


# ── TERM OF THE DAY ──

def _get_term_of_the_day() -> dict:
    all_terms = [entry for terms in GLOSSARY.values() for entry in terms]
    random.seed(date.today().toordinal())
    return random.choice(all_terms)


# ── CATEGORY BADGE ──

def _category_badge(category: str) -> str:
    return (
        f'<span style="background:#e8f4fd;color:#0c5460;padding:2px 10px;'
        f'border-radius:12px;font-size:11px;font-weight:500;">{category}</span>'
    )


# ── MAIN TAB ──

def show_glossary_tab(st) -> None:
    st.header("📖 Data Science Glossary")
    st.markdown("Your complete reference for data science terms — searchable, filterable, and AI-powered.")

    username = st.session_state.get("username", None)

    # ── TERM OF THE DAY ──
    tod = _get_term_of_the_day()
    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;
                    padding:1rem 1.4rem;border-radius:12px;margin-bottom:1.2rem;">
            <div style="font-size:11px;font-weight:700;letter-spacing:1px;
                        opacity:0.85;margin-bottom:4px;">✨ TERM OF THE DAY</div>
            <div style="font-size:18px;font-weight:700;margin-bottom:4px;">{tod['term']}</div>
            <div style="font-size:13px;opacity:0.9;line-height:1.5;">{tod['definition']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── SEARCH & FILTERS ──
    col1, col2, col3 = st.columns([3, 2, 2])
    with col1:
        query = st.text_input("🔍 Search a term...", placeholder="e.g. overfitting, precision, clustering")
    with col2:
        selected_category = st.selectbox("📂 Category", ["All"] + CATEGORIES)
    with col3:
        show_still_learning = st.checkbox("📌 Still Learning only", value=False)

    # ── AI DEFINITION LOOKUP ──
    st.markdown("---")
    with st.expander("🤖 Can't find your term? Ask AI to define it"):
        ai_term = st.text_input("Enter any data science term:", placeholder="e.g. SHAP values, Attention mechanism")
        if st.button("Generate Definition") and ai_term.strip():
            with st.spinner("Generating definition..."):
                try:
                    import anthropic
                    client = anthropic.Anthropic()
                    response = client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=200,
                        messages=[{
                            "role": "user",
                            "content": (
                                f"Define '{ai_term}' in data science in 2-3 sentences. "
                                "Be clear and beginner-friendly. No markdown, just plain text."
                            )
                        }]
                    )
                    st.success(f"**{ai_term}**")
                    st.write(response.content[0].text)
                    st.caption("💡 AI-generated definition — not yet in the main glossary.")
                except Exception:
                    st.warning("AI definition unavailable. Check your API key is configured.")

    st.markdown("---")

    # ── LOAD USER PROGRESS ──
    user_progress = _get_user_progress(username) if username else {}

    # ── FILTER TERMS ──
    all_terms = [entry for terms in GLOSSARY.values() for entry in terms]
    filtered = all_terms

    if query.strip():
        q = query.strip().lower()
        filtered = [e for e in filtered if q in e["term"].lower() or q in e["definition"].lower()]

    if selected_category != "All":
        filtered = [e for e in filtered if e["category"] == selected_category]

    if show_still_learning and username:
        filtered = [e for e in filtered if user_progress.get(e["term"]) == "still_learning"]

    total = sum(len(v) for v in GLOSSARY.values())
    known_count = sum(1 for v in user_progress.values() if v == "known")

    if username:
        st.markdown(f"**Showing {len(filtered)} of {total} terms** · ✅ {known_count} mastered")
    else:
        st.markdown(f"**Showing {len(filtered)} of {total} terms**")
        st.info("💡 Log in to track which terms you know and which you are still learning.")

    if not filtered:
        if show_still_learning:
            st.success("🎉 You have marked all filtered terms as known! Great work.")
        else:
            st.warning("No terms match your search. Try the AI definition lookup above!")
        return

    # ── DISPLAY TERMS ──
    if query.strip() or selected_category != "All" or show_still_learning:
        for entry in sorted(filtered, key=lambda x: x["term"]):
            _render_term_card(st, entry, username, user_progress)
    else:
        for letter in sorted(GLOSSARY.keys()):
            letter_terms = [e for e in GLOSSARY[letter] if e in filtered]
            if letter_terms:
                st.markdown(f"### {letter}")
                for entry in letter_terms:
                    _render_term_card(st, entry, username, user_progress)


# ── TERM CARD ──

def _render_term_card(st, entry: dict, username, user_progress: dict) -> None:
    term = entry["term"]
    status = user_progress.get(term, None)

    if status == "known":
        label = f"✅ **{term}**"
    elif status == "still_learning":
        label = f"📌 **{term}**"
    else:
        label = f"**{term}**"

    with st.expander(label):
        st.markdown(_category_badge(entry["category"]), unsafe_allow_html=True)
        st.markdown("")
        st.markdown(entry["definition"])

        if entry.get("related"):
            st.markdown(
                f"🔗 **Related terms:** {', '.join(f'`{t}`' for t in entry['related'])}"
            )

        if username:
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                if st.button(
                    "✅ I Know This" if status != "known" else "✅ Known",
                    key=f"known_{term}",
                    disabled=(status == "known"),
                    use_container_width=True,
                ):
                    _set_term_status(username, term, "known")
                    st.rerun()
            with col2:
                if st.button(
                    "📌 Still Learning" if status != "still_learning" else "📌 Marked",
                    key=f"learning_{term}",
                    disabled=(status == "still_learning"),
                    use_container_width=True,
                ):
                    _set_term_status(username, term, "still_learning")
                    st.rerun()
        else:
            st.caption("🔒 Log in to track your progress on this term.")
