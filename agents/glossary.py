# agents/glossary.py
import streamlit as st
import json
import os
from datetime import date

GLOSSARY_PROGRESS_FILE = "data/glossary_progress.json"

GLOSSARY = {
    # ── A ──
    "Accuracy": {
        "definition": "The proportion of correct predictions out of all predictions. Misleading when classes are imbalanced.",
        "category": "Evaluation",
        "related": ["Precision", "Recall", "F1 Score"],
        "example": "90% accuracy sounds great, but if 90% of data is class A, always predicting A achieves this without learning anything."
    },
    "Algorithm": {
        "definition": "A step-by-step procedure a computer follows to solve a problem or complete a task, such as training a machine learning model.",
        "category": "Core Concepts",
        "related": ["Model", "Machine Learning"],
        "example": "A recipe is like an algorithm — it gives exact steps to follow to produce a result."
    },
    "Anomaly Detection": {
        "definition": "The process of identifying unusual patterns or outliers in data that do not conform to expected behaviour.",
        "category": "ML Techniques",
        "related": ["Outlier", "Clustering"],
        "example": "A bank uses anomaly detection to flag a transaction of £5,000 when a customer usually spends £50."
    },
    "AutoML": {
        "definition": "Automated Machine Learning — automates the selection, training, and tuning of machine learning models with minimal human intervention.",
        "category": "ML Techniques",
        "related": ["Hyperparameter", "Model", "Cross-Validation"],
        "example": "DataForge's AutoML tab automatically tries multiple algorithms and picks the best one for your dataset."
    },
    # ── B ──
    "Bagging": {
        "definition": "An ensemble technique that trains multiple models on random subsets of the training data and combines their predictions to reduce variance.",
        "category": "ML Techniques",
        "related": ["Random Forest", "Ensemble Learning", "Overfitting"],
        "example": "Like asking 10 different doctors for a diagnosis — combining their opinions is more reliable than one alone."
    },
    "Bias": {
        "definition": "Systematic error in a dataset or model that produces unfair or inaccurate outcomes for certain groups.",
        "category": "Ethics",
        "related": ["Fairness", "Proxy Variable", "Class Imbalance"],
        "example": "A hiring model trained on historical data may disadvantage women if they were underrepresented in past hiring."
    },
    "Boosting": {
        "definition": "An ensemble method that trains models sequentially, where each model focuses on correcting the errors of the previous one.",
        "category": "ML Techniques",
        "related": ["Bagging", "Ensemble Learning", "XGBoost"],
        "example": "Like a student who reviews only the questions they got wrong each time — focusing on weak spots."
    },
    "Box Plot": {
        "definition": "A chart showing median, quartiles, and outliers for a numeric variable.",
        "category": "Visualisation",
        "related": ["IQR", "Outlier", "Median"],
        "example": "The box covers Q1 to Q3, the line is the median, and dots beyond the whiskers are outliers."
    },
    # ── C ──
    "Classification": {
        "definition": "A supervised learning task where the model predicts which category an input belongs to.",
        "category": "ML Techniques",
        "related": ["Regression", "Supervised Learning", "Label"],
        "example": "Predicting whether an email is spam or not spam is a binary classification problem."
    },
    "Clustering": {
        "definition": "An unsupervised learning technique that groups similar data points together without predefined labels.",
        "category": "ML Techniques",
        "related": ["K-Means", "Unsupervised Learning"],
        "example": "A supermarket uses clustering to group customers with similar buying habits for targeted marketing."
    },
    "Confusion Matrix": {
        "definition": "A table comparing predicted labels against actual labels across True Positives, False Positives, True Negatives, and False Negatives.",
        "category": "Evaluation",
        "related": ["Accuracy", "Precision", "Recall"],
        "example": "A confusion matrix for a disease test shows how many patients were correctly diagnosed vs misdiagnosed."
    },
    "Correlation": {
        "definition": "Measures the strength and direction of a linear relationship between two variables. r ranges from -1 to +1.",
        "category": "Statistics",
        "related": ["Causation", "Scatter Plot", "Multicollinearity"],
        "example": "r = 0.9 between hours studied and exam score means a strong positive relationship — more study, higher score."
    },
    "Cross-Validation": {
        "definition": "A technique to estimate model performance by splitting data into multiple train/test subsets and averaging results.",
        "category": "Evaluation",
        "related": ["Train/Test Split", "Overfitting", "Generalisation"],
        "example": "5-fold CV splits data into 5 parts, trains on 4, tests on 1, repeated 5 times — more reliable than one split."
    },
    # ── D ──
    "Data Cleaning": {
        "definition": "The process of detecting and fixing errors, missing values, duplicates, and inconsistencies in a dataset.",
        "category": "Data Science",
        "related": ["Missing Values", "Outlier", "Imputation"],
        "example": "Removing duplicate rows, filling missing ages with the median, and standardising column name formats."
    },
    "Data Leakage": {
        "definition": "When information from outside the training dataset is used to create the model, leading to unrealistically high performance.",
        "category": "Core Concepts",
        "related": ["Overfitting", "Train/Test Split"],
        "example": "Using tomorrow's stock price to predict today's movement — the model can't know this in production."
    },
    "Decision Tree": {
        "definition": "A model that splits data into branches based on feature values, making decisions at each node until reaching a prediction.",
        "category": "ML Techniques",
        "related": ["Random Forest", "Overfitting"],
        "example": "A decision tree for loan approval might first ask: income > £30k? Then: credit score > 700? Then: approve/reject."
    },
    "Dimensionality Reduction": {
        "definition": "Techniques that reduce the number of features in a dataset while preserving important information.",
        "category": "Data Science",
        "related": ["PCA", "Feature Selection"],
        "example": "Compressing 100 features down to 10 key components while keeping 95% of the information."
    },
    # ── E ──
    "EDA": {
        "definition": "Exploratory Data Analysis — the process of summarising and visualising data to discover patterns before modelling.",
        "category": "Data Science",
        "related": ["Data Cleaning", "Visualisation", "Statistics"],
        "example": "Plotting distributions, checking correlations, and identifying outliers before building any model."
    },
    "Ensemble Learning": {
        "definition": "Combining multiple machine learning models to produce better predictions than any single model alone.",
        "category": "ML Techniques",
        "related": ["Bagging", "Boosting", "Random Forest"],
        "example": "Asking 100 experts and taking a majority vote instead of relying on one expert's opinion."
    },
    "EU AI Act": {
        "definition": "European regulation (2024) requiring AI systems to be transparent, explainable, and free from discriminatory bias.",
        "category": "Ethics",
        "related": ["Bias", "Fairness", "Explainability"],
        "example": "A hospital using AI for diagnosis must document bias checks and provide explanations for decisions."
    },
    # ── F ──
    "F1 Score": {
        "definition": "The harmonic mean of Precision and Recall. A balanced metric useful when class distribution is uneven.",
        "category": "Evaluation",
        "related": ["Precision", "Recall", "Accuracy"],
        "example": "A spam detector with F1=0.95 means it rarely misses spam and rarely flags normal emails as spam."
    },
    "Fairness": {
        "definition": "The principle that AI systems should treat all individuals and groups equitably without discrimination.",
        "category": "Ethics",
        "related": ["Bias", "EU AI Act", "Protected Characteristics"],
        "example": "A loan model should not reject applications based on postcode as a proxy for race."
    },
    "Feature": {
        "definition": "An individual measurable property or characteristic of the data used as input to a machine learning model.",
        "category": "Core Concepts",
        "related": ["Feature Engineering", "Target Variable"],
        "example": "In a house price model, features include: number of bedrooms, location, and floor area."
    },
    "Feature Engineering": {
        "definition": "The process of using domain knowledge to create, transform, or select features that improve a model's performance.",
        "category": "Data Science",
        "related": ["Feature", "Feature Selection"],
        "example": "Creating an 'age_group' column from raw age values to help the model find patterns more easily."
    },
    "Feature Importance": {
        "definition": "A score indicating how much each input column contributed to a model's predictions.",
        "category": "ML Techniques",
        "related": ["Random Forest", "Gradient Boosting", "Feature Selection"],
        "example": "Feature importance of 0.45 for 'age' means age was the most influential predictor in the model."
    },
    # ── G ──
    "Gradient Descent": {
        "definition": "An optimisation algorithm that iteratively adjusts model parameters to minimise the loss function.",
        "category": "Deep Learning",
        "related": ["Loss Function", "Neural Network", "Epoch"],
        "example": "Like rolling a ball downhill — each step moves parameters in the direction that reduces error."
    },
    # ── H ──
    "Heatmap": {
        "definition": "A colour-coded matrix showing values — commonly used to visualise correlation matrices.",
        "category": "Visualisation",
        "related": ["Correlation", "Matrix"],
        "example": "Dark green cells in a correlation heatmap indicate strong positive correlations between variables."
    },
    "Histogram": {
        "definition": "A bar chart showing the frequency distribution of a numeric variable, divided into bins.",
        "category": "Visualisation",
        "related": ["Distribution", "Skewness"],
        "example": "A histogram of customer ages shows most customers are between 25 and 45."
    },
    "Hyperparameter": {
        "definition": "A parameter set before training a model that controls the learning process. Different from parameters learned during training.",
        "category": "ML Techniques",
        "related": ["Model", "Cross-Validation", "AutoML"],
        "example": "The number of trees in a Random Forest is a hyperparameter — you set it before training begins."
    },
    # ── I ──
    "IQR": {
        "definition": "Interquartile Range — the difference between Q3 and Q1. Used to detect outliers.",
        "category": "Statistics",
        "related": ["Quartile", "Outlier", "Box Plot"],
        "example": "Values outside Q1 - 1.5×IQR or Q3 + 1.5×IQR are flagged as potential outliers."
    },
    "Imputation": {
        "definition": "The process of replacing missing values with substituted values such as the mean, median, or a predicted value.",
        "category": "Data Science",
        "related": ["Missing Values", "Data Cleaning"],
        "example": "Filling 40 missing age values with the median age of 34 to keep those rows usable."
    },
    # ── K ──
    "K-Means": {
        "definition": "A clustering algorithm that partitions data into K groups by minimising the distance between data points and their cluster centre.",
        "category": "ML Techniques",
        "related": ["Clustering", "Unsupervised Learning"],
        "example": "Grouping 10,000 customers into 5 segments based on their purchasing behaviour."
    },
    "K-Nearest Neighbours (KNN)": {
        "definition": "A classification algorithm that assigns a label based on the majority label of its K nearest neighbours in feature space.",
        "category": "ML Techniques",
        "related": ["Classification", "Supervised Learning"],
        "example": "To classify a new flower, KNN looks at the 5 most similar flowers it has seen before and votes."
    },
    "Kaggle": {
        "definition": "The world's largest platform for data science datasets and competitions, used by over 15 million data scientists.",
        "category": "Tools",
        "related": ["Dataset"],
        "example": "DataForge connects to Kaggle so students can import real world datasets without leaving the app."
    },
    # ── L ──
    "Label": {
        "definition": "The target output value in a supervised learning dataset — what the model is trying to predict.",
        "category": "Core Concepts",
        "related": ["Classification", "Supervised Learning", "Target Variable"],
        "example": "In an email dataset, the label is 'spam' or 'not spam' — the answer the model must learn to predict."
    },
    "LangChain": {
        "definition": "A framework for building applications powered by large language models.",
        "category": "Tools",
        "related": ["GPT-4", "Multi-Agent", "Orchestrator"],
        "example": "DataForge uses LangChain to coordinate its pipeline agents and route user requests intelligently."
    },
    "Linear Regression": {
        "definition": "A model that predicts a continuous numeric output by fitting a straight line through the data.",
        "category": "ML Techniques",
        "related": ["Regression", "Loss Function"],
        "example": "Predicting house price based on floor area — more square metres, higher price, modelled as a straight line."
    },
    "Logistic Regression": {
        "definition": "Despite the name, a classification algorithm that predicts the probability of a binary outcome using a sigmoid function.",
        "category": "ML Techniques",
        "related": ["Classification", "Linear Regression"],
        "example": "Predicting the probability that a student passes (1) or fails (0) based on hours studied."
    },
    "Loss Function": {
        "definition": "A function that measures how far a model's predictions are from the true values. The model is trained by minimising this.",
        "category": "Core Concepts",
        "related": ["Gradient Descent", "Overfitting"],
        "example": "Mean Squared Error measures the average squared difference between predicted and actual house prices."
    },
    # ── M ──
    "Machine Learning": {
        "definition": "A branch of AI where systems learn patterns from data and improve their performance without being explicitly programmed.",
        "category": "Core Concepts",
        "related": ["Algorithm", "Model", "Deep Learning"],
        "example": "A spam filter learns from thousands of emails to identify patterns without being told specific rules."
    },
    "Mean": {
        "definition": "The arithmetic average — sum of all values divided by the count. Sensitive to outliers.",
        "category": "Statistics",
        "related": ["Median", "Mode", "Standard Deviation"],
        "example": "Mean income of [20k, 30k, 100k] = 50k — distorted by the high earner."
    },
    "Median": {
        "definition": "The middle value when data is sorted. Robust to outliers — preferred for skewed distributions.",
        "category": "Statistics",
        "related": ["Mean", "Skewness", "IQR"],
        "example": "Median income of [20k, 30k, 100k] = 30k — not affected by the high earner."
    },
    "Missing Values": {
        "definition": "Cells with no data — represented as NaN, null, or blank. Must be handled before analysis or modelling.",
        "category": "Data Science",
        "related": ["Imputation", "Data Cleaning"],
        "example": "40 missing values in the age column — filled using median imputation to avoid losing those rows."
    },
    "Model": {
        "definition": "A mathematical representation of a pattern in data, trained on examples and used to make predictions on new data.",
        "category": "Core Concepts",
        "related": ["Algorithm", "Machine Learning"],
        "example": "A trained model that predicts loan default risk based on income, age, and credit history."
    },
    "Multicollinearity": {
        "definition": "When two or more features are highly correlated with each other, making it hard to determine their individual effects.",
        "category": "Statistics",
        "related": ["Correlation", "Feature Selection"],
        "example": "Height and shoe size are correlated — including both in a model may cause multicollinearity issues."
    },
    # ── N ──
    "Neural Network": {
        "definition": "A computing system loosely inspired by the human brain, consisting of layers of interconnected nodes that learn from data.",
        "category": "Deep Learning",
        "related": ["Deep Learning", "Epoch", "Gradient Descent"],
        "example": "A neural network recognises handwritten digits by learning pixel patterns from thousands of examples."
    },
    "Normal Distribution": {
        "definition": "A symmetric bell-shaped distribution where most values cluster around the mean.",
        "category": "Statistics",
        "related": ["Mean", "Standard Deviation", "Skewness"],
        "example": "Heights of adults approximately follow a normal distribution — most near the average, few very tall or short."
    },
    "Normalisation": {
        "definition": "Scaling numerical features to a standard range (usually 0 to 1) so no single feature dominates due to its magnitude.",
        "category": "Data Science",
        "related": ["Standardisation", "Feature Engineering"],
        "example": "Age (0-100) and income (0-100,000) are on very different scales — normalisation brings them to the same range."
    },
    "Null Value": {
        "definition": "A missing or undefined value in a dataset, often represented as NaN (Not a Number) in Python's Pandas library.",
        "category": "Data Science",
        "related": ["Missing Values", "Imputation"],
        "example": "df.isnull().sum() shows how many null values exist in each column of your DataFrame."
    },
    # ── O ──
    "Outlier": {
        "definition": "A data point significantly different from other observations. Detected using IQR or Z-score methods.",
        "category": "Statistics",
        "related": ["IQR", "Box Plot", "Data Cleaning"],
        "example": "An income of £2,000,000 in a dataset of typical salaries is an outlier that could distort analysis."
    },
    "Overfitting": {
        "definition": "When a model learns the training data too well including noise and fails to generalise to new data.",
        "category": "Core Concepts",
        "related": ["Underfitting", "Cross-Validation", "Regularisation"],
        "example": "A student who memorises exam answers but cannot apply knowledge to new questions — performs perfectly in training, fails in testing."
    },
    # ── P ──
    "P-value": {
        "definition": "The probability of observing results as extreme as the data, assuming the null hypothesis is true. p < 0.05 is typically significant.",
        "category": "Statistics",
        "related": ["Hypothesis Testing", "Null Hypothesis", "Confidence Interval"],
        "example": "p = 0.03 means there is a 3% chance the result occurred by random chance — statistically significant."
    },
    "Pandas": {
        "definition": "A Python library for data manipulation and analysis — provides DataFrame structures for tabular data.",
        "category": "Tools",
        "related": ["NumPy", "DataFrame", "Python"],
        "example": "df.dropna() removes rows with missing values. df.describe() gives summary statistics instantly."
    },
    "Plotly": {
        "definition": "A Python library for creating interactive charts.",
        "category": "Tools",
        "related": ["Matplotlib", "Seaborn", "Visualisation"],
        "example": "DataForge uses Plotly so students can hover over data points for details and zoom into charts."
    },
    "Precision": {
        "definition": "The proportion of positive predictions that were actually correct. Important when false positives are costly.",
        "category": "Evaluation",
        "related": ["Recall", "F1 Score", "Confusion Matrix"],
        "example": "A cancer test with 99% precision means 99% of positive results are true cases — very few false alarms."
    },
    "Principal Component Analysis (PCA)": {
        "definition": "A dimensionality reduction technique that transforms features into uncorrelated components capturing maximum variance.",
        "category": "ML Techniques",
        "related": ["Dimensionality Reduction", "Feature Selection"],
        "example": "Compressing 50 features into 5 principal components that explain 90% of the variance in the data."
    },
    "Proxy Variable": {
        "definition": "A variable correlated with a protected attribute that can introduce bias into a model even when the protected attribute is excluded.",
        "category": "Ethics",
        "related": ["Bias", "Fairness", "Feature"],
        "example": "Postcode can be a proxy for race — excluding race but including postcode may still produce a biased model."
    },
    # ── R ──
    "Random Forest": {
        "definition": "An ensemble method that builds many decision trees and combines their predictions by majority vote or averaging.",
        "category": "ML Techniques",
        "related": ["Decision Tree", "Bagging", "Ensemble Learning"],
        "example": "Asking 100 experts and taking a majority vote instead of relying on one expert's opinion."
    },
    "Recall": {
        "definition": "The proportion of actual positives correctly identified by the model. Important when false negatives are costly.",
        "category": "Evaluation",
        "related": ["Precision", "F1 Score", "Confusion Matrix"],
        "example": "A fraud detector with high recall catches most fraud cases — missing fraud is more costly than a false alarm."
    },
    "Regression": {
        "definition": "A supervised learning task where the model predicts a continuous numeric output.",
        "category": "ML Techniques",
        "related": ["Classification", "Linear Regression"],
        "example": "Predicting house prices, temperatures, or exam scores are all regression problems."
    },
    "ROC-AUC": {
        "definition": "Area Under the ROC Curve — measures a model's ability to distinguish between classes across all classification thresholds.",
        "category": "Evaluation",
        "related": ["Precision", "Recall", "Accuracy"],
        "example": "AUC = 0.97 means the model correctly ranks a positive case above a negative case 97% of the time."
    },
    # ── S ──
    "Scikit-learn": {
        "definition": "The most widely used Python machine learning library — provides tools for classification, regression, clustering and preprocessing.",
        "category": "Tools",
        "related": ["Python", "Machine Learning", "Pandas"],
        "example": "DataForge AutoML agent uses scikit-learn to train and compare multiple algorithms on your dataset."
    },
    "Skewness": {
        "definition": "Measures the asymmetry of a distribution. Positive skew = long right tail. Negative skew = long left tail.",
        "category": "Statistics",
        "related": ["Normal Distribution", "Mean", "Median"],
        "example": "Income data is positively skewed — most earn average wages but a few earn millions, pulling the tail right."
    },
    "Standard Deviation": {
        "definition": "Measures how spread out values are around the mean. Large std = high variability.",
        "category": "Statistics",
        "related": ["Mean", "Variance", "Normal Distribution"],
        "example": "Heights: mean=170cm, std=5cm means most people are between 165-175cm."
    },
    "Standardisation": {
        "definition": "Scaling features so they have a mean of 0 and standard deviation of 1. Makes features comparable regardless of units.",
        "category": "Data Science",
        "related": ["Normalisation", "Feature Engineering"],
        "example": "Standardising age and income puts them on the same scale so neither dominates the model."
    },
    "Streamlit": {
        "definition": "A Python framework for building and deploying interactive web applications for data science.",
        "category": "Tools",
        "related": ["Python", "Plotly", "Deployment"],
        "example": "DataForge is built entirely with Streamlit — turning Python scripts into an interactive web app."
    },
    "Supervised Learning": {
        "definition": "A type of machine learning where the model is trained on labelled data — each input has a known correct output.",
        "category": "Core Concepts",
        "related": ["Unsupervised Learning", "Classification", "Regression"],
        "example": "Training a model on 10,000 labelled emails (spam/not spam) so it can classify new emails."
    },
    "Support Vector Machine (SVM)": {
        "definition": "A classification algorithm that finds the optimal boundary separating classes in feature space with the maximum margin.",
        "category": "ML Techniques",
        "related": ["Classification"],
        "example": "SVM draws the widest possible boundary between cats and dogs in feature space to classify new images."
    },
    # ── T ──
    "Target Variable": {
        "definition": "The output variable that a machine learning model is trained to predict. Also called label, dependent variable, or response variable.",
        "category": "Core Concepts",
        "related": ["Feature", "Label", "Supervised Learning"],
        "example": "In a house price model, the target variable is 'price' — everything else is a feature."
    },
    "Train/Test Split": {
        "definition": "Dividing a dataset into a training set used to train the model and a test set used to evaluate it on unseen data.",
        "category": "Evaluation",
        "related": ["Cross-Validation", "Overfitting"],
        "example": "80% of data used to train the model, 20% held back to test how well it performs on new data."
    },
    "Transfer Learning": {
        "definition": "Using a model pre-trained on one task as the starting point for a model on a different but related task.",
        "category": "Deep Learning",
        "related": ["Neural Network"],
        "example": "A model trained on millions of images is fine-tuned to recognise specific medical scans."
    },
    # ── U ──
    "Underfitting": {
        "definition": "When a model is too simple to capture patterns in the data, resulting in poor performance on both training and test data.",
        "category": "Core Concepts",
        "related": ["Overfitting", "Bias"],
        "example": "A linear model trying to fit a curved relationship will underfit — the line misses the pattern entirely."
    },
    "Unsupervised Learning": {
        "definition": "A type of machine learning where the model is trained on unlabelled data and must find patterns or structure on its own.",
        "category": "Core Concepts",
        "related": ["Supervised Learning", "Clustering"],
        "example": "Grouping customers by behaviour without being told what the groups should be in advance."
    },
    # ── V ──
    "Variance": {
        "definition": "A measure of how much a model's predictions fluctuate for different training datasets. High variance causes overfitting.",
        "category": "Core Concepts",
        "related": ["Bias", "Overfitting", "Standard Deviation"],
        "example": "A model that performs perfectly on training data but poorly on test data has high variance."
    },
    "Visualisation": {
        "definition": "The representation of data through charts, graphs, and plots to help identify patterns and outliers not obvious in raw numbers.",
        "category": "Data Science",
        "related": ["EDA", "Histogram", "Box Plot", "Heatmap"],
        "example": "A scatter plot reveals a strong correlation between two variables that a table of numbers would hide."
    },
    # ── X ──
    "XGBoost": {
        "definition": "An optimised gradient boosting algorithm known for its speed and performance. Widely used in data science competitions.",
        "category": "ML Techniques",
        "related": ["Boosting", "Ensemble Learning", "Random Forest"],
        "example": "XGBoost consistently wins Kaggle competitions — it combines speed, accuracy, and handling of missing values."
    },
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
                "content": "You are a data science educator. Define the term in 2-3 sentences with one real world example. Format: Definition: ... | Example: ... | Related: term1, term2"
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

    # ── TERM OF THE DAY ──
    term_name, term_data = get_term_of_the_day()
    st.markdown(
        f'<div style="background:linear-gradient(135deg,#028090,#02C39A);'
        f'border-radius:12px;padding:1.2rem 1.5rem;margin-bottom:1rem">'
        f'<div style="color:white;font-size:.8rem;font-weight:bold;text-transform:uppercase">✨ Term of the Day</div>'
        f'<div style="color:white;font-size:1.4rem;font-weight:900;margin:.3rem 0">{term_name}</div>'
        f'<div style="color:rgba(255,255,255,.9);font-size:.95rem">{term_data["definition"]}</div>'
        f'<div style="color:rgba(255,255,255,.7);font-size:.82rem;margin-top:.5rem">'
        f'📌 {term_data.get("example","")}</div>'
        f'</div>', unsafe_allow_html=True)

    st.divider()

    # ── SEARCH & FILTERS ──
    col_s, col_c = st.columns([3, 2])
    with col_s:
        search = st.text_input("Search terms", placeholder="e.g. correlation, overfitting...",
                                key="glossary_search", label_visibility="collapsed")
    with col_c:
        categories = ["All"] + get_categories()
        cat_filter = st.selectbox("Filter by category", categories,
                                   key="glossary_cat", label_visibility="collapsed")

    # ── STILL LEARNING FILTER ──
    statuses = get_term_statuses(username) if username else {}
    show_learning = st.checkbox("📚 Show 'Still Learning' terms only", value=False)

    # ── FILTER TERMS ──
    filtered = {}
    for term, data in sorted(GLOSSARY.items()):
        if search and search.lower() not in term.lower() and search.lower() not in data["definition"].lower():
            continue
        if cat_filter != "All" and data["category"] != cat_filter:
            continue
        if show_learning and username:
            if statuses.get(term) != "learning":
                continue
        filtered[term] = data

    # ── STATS BAR ──
    st.markdown(f"**{len(filtered)} term(s)** | "
                f"✅ {sum(1 for s in statuses.values() if s=='know')} known · "
                f"📚 {sum(1 for s in statuses.values() if s=='learning')} still learning")

    if not filtered:
        if show_learning:
            st.success("🎉 You've marked all terms as known! Great work.")
        else:
            st.warning("No terms match your search.")
        return

    st.divider()

    # ── A-Z GROUPED DISPLAY ──
    current_letter = ""
    for term, data in filtered.items():
        first_letter = term[0].upper()
        if first_letter != current_letter:
            current_letter = first_letter
            st.markdown(f"### {current_letter}")

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
            else:
                st.caption("🔒 Log in to track your progress on this term.")

    st.divider()

    # ── AI DEFINITION LOOKUP ──
    st.markdown("### 🤖 AI Definition Lookup")
    st.markdown("Can't find a term? Ask GPT-4 for an instant definition.")
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
