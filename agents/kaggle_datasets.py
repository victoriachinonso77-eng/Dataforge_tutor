# agents/kaggle_datasets.py — Upgraded Kaggle Dataset Explorer

import streamlit as st

# ── CURATED DATASETS ──
CURATED_DATASETS = {
    "classification": [
        {"name": "Titanic Survival Prediction", "rows": "891", "cols": "12",
         "description": "Predict who survived the Titanic disaster. Classic beginner dataset.",
         "url": "https://www.kaggle.com/datasets/yasserh/titanic-dataset",
         "difficulty": "Beginner", "topic": "Classification"},
        {"name": "Iris Flower Classification", "rows": "150", "cols": "5",
         "description": "Classify iris flowers into 3 species based on petal measurements.",
         "url": "https://www.kaggle.com/datasets/arshid/iris-flower-dataset",
         "difficulty": "Beginner", "topic": "Classification"},
        {"name": "Heart Disease Prediction", "rows": "303", "cols": "14",
         "description": "Predict presence of heart disease using patient medical records.",
         "url": "https://www.kaggle.com/datasets/johnsmith88/heart-disease-dataset",
         "difficulty": "Beginner", "topic": "Classification"},
        {"name": "Credit Card Fraud Detection", "rows": "284,807", "cols": "31",
         "description": "Detect fraudulent credit card transactions. Real anonymised data.",
         "url": "https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud",
         "difficulty": "Intermediate", "topic": "Classification"},
    ],
    "regression": [
        {"name": "House Prices Prediction", "rows": "1,460", "cols": "81",
         "description": "Predict house sale prices in Ames, Iowa. Many numeric features.",
         "url": "https://www.kaggle.com/competitions/house-prices-advanced-regression-techniques",
         "difficulty": "Beginner", "topic": "Regression"},
        {"name": "Medical Cost Prediction", "rows": "1,338", "cols": "7",
         "description": "Predict insurance charges from age, BMI, smoking status.",
         "url": "https://www.kaggle.com/datasets/mirichoi0218/insurance",
         "difficulty": "Beginner", "topic": "Regression"},
        {"name": "Car Price Prediction", "rows": "205", "cols": "26",
         "description": "Predict car prices from specifications and features.",
         "url": "https://www.kaggle.com/datasets/hellbuoy/car-price-prediction",
         "difficulty": "Beginner", "topic": "Regression"},
    ],
    "clustering": [
        {"name": "Customer Segmentation", "rows": "200", "cols": "5",
         "description": "Segment mall customers by spending behaviour and income.",
         "url": "https://www.kaggle.com/datasets/vjchoudhary7/customer-segmentation-tutorial-in-python",
         "difficulty": "Beginner", "topic": "Clustering"},
        {"name": "Online Retail Dataset", "rows": "541,909", "cols": "8",
         "description": "UK retail transactions for customer lifetime value analysis.",
         "url": "https://www.kaggle.com/datasets/lakshmi25npathi/online-retail-dataset",
         "difficulty": "Intermediate", "topic": "Clustering"},
    ],
    "time_series": [
        {"name": "Superstore Sales", "rows": "9,994", "cols": "21",
         "description": "Retail sales data with dates for time series forecasting.",
         "url": "https://www.kaggle.com/datasets/vivek468/superstore-dataset-final",
         "difficulty": "Beginner", "topic": "Time Series"},
        {"name": "Air Quality Index", "rows": "4,344", "cols": "15",
         "description": "Daily air quality measurements for forecasting.",
         "url": "https://www.kaggle.com/datasets/rohanrao/air-quality-data-in-india",
         "difficulty": "Intermediate", "topic": "Time Series"},
    ],
    "education": [
        {"name": "Student Performance", "rows": "395", "cols": "33",
         "description": "Predict student grades based on demographics and study habits.",
         "url": "https://www.kaggle.com/datasets/impapan/student-performance-data-set",
         "difficulty": "Beginner", "topic": "Education"},
        {"name": "PISA Scores", "rows": "4,841", "cols": "12",
         "description": "International student assessment scores across countries.",
         "url": "https://www.kaggle.com/datasets/econdata/pisa-test-scores",
         "difficulty": "Intermediate", "topic": "Education"},
    ],
}

TOPIC_ICONS = {
    "classification": "🎯",
    "regression": "📈",
    "clustering": "🔵",
    "time_series": "⏱️",
    "education": "🎓",
}


# ── ORIGINAL FUNCTIONS (kept for backward compatibility) ──

def recommend_datasets(learning_goal: str = "classification",
                       level: str = "beginner") -> list:
    goal_lower = learning_goal.lower()
    category = "classification"
    if "regress" in goal_lower or "price" in goal_lower:
        category = "regression"
    elif "cluster" in goal_lower or "segment" in goal_lower or "group" in goal_lower:
        category = "clustering"
    elif "time" in goal_lower or "series" in goal_lower or "forecast" in goal_lower:
        category = "time_series"
    elif "education" in goal_lower or "student" in goal_lower or "school" in goal_lower:
        category = "education"
    datasets = CURATED_DATASETS.get(category, CURATED_DATASETS["classification"])
    if level == "beginner":
        datasets = [d for d in datasets if d["difficulty"] == "Beginner"]
    return datasets


def render_dataset_cards(st, datasets: list) -> None:
    """Original basic card renderer — kept for backward compatibility."""
    for i, ds in enumerate(datasets):
        with st.container():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{ds['name']}**")
                st.caption(f"📊 {ds['rows']} rows · {ds['cols']} columns · "
                           f"🎯 {ds['difficulty']} · 📁 {ds['topic']}")
                st.markdown(f"_{ds['description']}_")
            with col2:
                st.link_button("View on Kaggle", ds["url"])
            if i < len(datasets) - 1:
                st.divider()


# ── AI RECOMMENDATION ──

def generate_ai_recommendation(client, user_goal):
    if not client:
        return None
    try:
        all_datasets = []
        for topic, datasets in CURATED_DATASETS.items():
            for ds in datasets:
                all_datasets.append(
                    f"- {ds['name']} ({ds['topic']}, {ds['difficulty']}): {ds['description']}"
                )
        prompt = f"""You are a data science tutor helping a student find the right dataset.

The student said: "{user_goal}"

Here are the available datasets:
{chr(10).join(all_datasets)}

Recommend the 3 most suitable datasets for the student's goal.
For each one explain in 1-2 sentences why it is perfect for their goal.
Be friendly, specific, and educational. No markdown, just plain text with numbered points."""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"AI recommendation unavailable: {e}"


# ── UPGRADED MAIN TAB ──

def render_kaggle_tab(gpt_client=None):
    st.markdown("### 🔍 Kaggle Dataset Explorer")
    st.markdown("Find a free dataset to practise with — browse by topic or get an AI recommendation.")

    k1, k2 = st.tabs(["📚 Browse Datasets", "🤖 AI Recommender"])

    # ── BROWSE TAB ──
    with k1:
        st.markdown("**Find a free dataset on Kaggle to practise with:**")
        st.markdown("**What do you want to learn?**")

        # ── USE RADIO BUTTONS INSTEAD OF SELECTBOX ──
        goal = st.radio(
            "Select a topic:",
            options=list(CURATED_DATASETS.keys()),
            format_func=lambda x: f"{TOPIC_ICONS.get(x, '📂')} {x.replace('_', ' ').title()}",
            horizontal=True,
            key="kaggle_goal",
            label_visibility="collapsed"
        )

        st.divider()

        datasets = recommend_datasets(goal)
        icon = TOPIC_ICONS.get(goal, "📂")
        st.markdown(f"#### {icon} {goal.replace('_', ' ').title()} Datasets")

        for i, ds in enumerate(datasets):
            with st.expander(f"**{ds['name']}**"):
                st.markdown(f"_{ds['description']}_")
                st.markdown(
                    f"📊 **{ds['rows']} rows** · **{ds['cols']} columns** · 📁 {ds['topic']}"
                )

                col_a, col_b = st.columns(2)
                with col_a:
                    st.link_button(
                        "🔗 View on Kaggle",
                        ds["url"],
                        use_container_width=True
                    )
                with col_b:
                    if st.button(
                        "💡 Why use this?",
                        key=f"why_{goal}_{i}",
                        use_container_width=True
                    ):
                        if gpt_client:
                            with st.spinner("GPT-4 is explaining..."):
                                try:
                                    response = gpt_client.chat.completions.create(
                                        model="gpt-4",
                                        messages=[{"role": "user", "content": (
                                            f"In 2-3 sentences, explain why a data science student "
                                            f"should use the '{ds['name']}' dataset and what key "
                                            f"skills they will learn from it. Be friendly and educational."
                                        )}],
                                        max_tokens=150
                                    )
                                    st.info(response.choices[0].message.content.strip())
                                except Exception as e:
                                    st.warning(f"GPT-4 unavailable: {e}")
                        else:
                            st.info("💡 Add your OpenAI API key to enable AI explanations.")

    # ── AI RECOMMENDER TAB ──
    with k2:
        st.markdown("#### 🤖 AI Dataset Recommender")
        st.markdown(
            "Describe what you want to learn and GPT-4 will recommend "
            "the best datasets from our curated library."
        )

        user_goal = st.text_area(
            "What do you want to learn or analyse?",
            placeholder=(
                "e.g. I want to practise predicting house prices using regression...\n"
                "or I want to explore customer behaviour using clustering...\n"
                "or I want to build a classification model for medical data..."
            ),
            height=120,
            key="ai_goal_input"
        )

        if st.button("🤖 Get AI Recommendation", use_container_width=True) and user_goal.strip():
            st.divider()
            st.markdown("**📚 Curated Recommendations:**")
            curated = recommend_datasets(user_goal)
            if curated:
                render_dataset_cards(st, curated[:3])
            else:
                st.info("No curated matches found.")

            if gpt_client:
                st.divider()
                st.markdown("**🤖 AI Explanation:**")
                with st.spinner("GPT-4 is finding the best datasets for you..."):
                    recommendation = generate_ai_recommendation(gpt_client, user_goal.strip())
                if recommendation:
                    st.markdown(
                        f'<div style="background:#161B22;border-left:4px solid #02C39A;'
                        f'padding:1rem 1.4rem;border-radius:0 8px 8px 0;color:#E6EDF3;'
                        f'font-size:.95rem;line-height:1.8">'
                        f'🤖 {recommendation.replace(chr(10), "<br>")}</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.info("💡 Add your OpenAI API key to get personalised AI explanations.")
