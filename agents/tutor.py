# agents/tutor.py
# DataForge Tutor Agent — Teaches data science concepts at each pipeline stage

LESSONS = {
    "beginner": {
        "intro": """
## 👋 Welcome to DataForge — Your Data Science Tutor!

Before we start, let's understand what **data science** is.

> 📖 **Data Science** is the process of collecting raw data, cleaning it, analysing it, 
> visualising it, and drawing conclusions from it — to help make better decisions.

Think of it like this: imagine you have a messy notebook full of numbers. 
A data scientist's job is to:
1. **Clean** the notebook (fix errors, fill gaps)
2. **Read** the notebook (find patterns and statistics)
3. **Draw** the notebook (make charts to see trends)
4. **Explain** the notebook (write a summary of findings)

DataForge will do all of this automatically — but more importantly, it will **explain 
every single step** so you learn exactly what is happening and why. Let's begin! 🚀
""",
        "cleaning": {
            "intro": """
## 🧹 Step 1: Data Cleaning

### What is Data Cleaning?
Real-world datasets are almost never perfect. They usually have:

| Problem | Example | Why it matters |
|---|---|---|
| **Missing values** | A cell with no data | Can cause errors in calculations |
| **Duplicate rows** | Same row appearing twice | Skews your results |
| **Wrong column names** | "First Name " (with a space) | Hard to work with in code |
| **Outliers** | A salary of £999,999,999 | Can distort averages |

> 💡 **Key Concept:** Garbage in = Garbage out. If your data is messy, 
> your analysis will be wrong — no matter how good your code is.

**DataForge is now cleaning your dataset. Watch what it finds...**
""",
            "missing_values": """
### 🔧 Handling Missing Values
A **missing value** (also called NaN — "Not a Number") is an empty cell in your data.

**Why do they appear?**
- Someone forgot to fill in a form
- A sensor failed to record a reading
- Data was lost during export

**How DataForge fixes them:**
- For **numbers**: fills with the **median** (middle value) — more robust than the average
- For **text**: fills with the **mode** (most common value)

> 💡 **Why median and not average?** If most people earn £30,000 but one person 
> earns £10,000,000, the average is misleading. The median ignores extremes.
""",
            "duplicates": """
### 🗑️ Removing Duplicate Rows
A **duplicate row** is when the exact same data appears more than once.

**Why are they dangerous?**
- They make your dataset appear bigger than it is
- They inflate counts and totals
- They can bias your machine learning models

**DataForge removes them automatically** and tells you exactly how many were found.
""",
            "outliers": """
### ⚠️ Detecting Outliers
An **outlier** is a data point that is very different from the others.

**How DataForge detects them — The IQR Method:**
```
Q1 = 25th percentile (bottom quarter of values)
Q3 = 75th percentile (top quarter of values)  
IQR = Q3 - Q1 (the middle spread)

Outlier if: value < Q1 - 1.5×IQR  OR  value > Q3 + 1.5×IQR
```

> 💡 **Important:** DataForge **flags** outliers but does NOT delete them.
> In fraud detection, outliers ARE the interesting data!
> Always decide yourself whether to remove them.
"""
        },
        "analysis": {
            "intro": """
## 📊 Step 2: Statistical Analysis

### What is Statistics?
Statistics is the science of making sense of numbers.

After cleaning, DataForge calculates these key statistics for every numeric column:

| Statistic | What it means | Example |
|---|---|---|
| **Mean** | The average | Average age = 35 |
| **Median** | The middle value | Middle salary = £28,000 |
| **Std Dev** | How spread out the data is | Ages vary by ±12 years |
| **Min / Max** | Smallest and largest values | Ages range from 18 to 85 |

### What is Correlation?
**Correlation** measures whether two columns are related.

- **r = +1.0**: Perfect positive relationship (as X goes up, Y goes up)
- **r = -1.0**: Perfect negative relationship (as X goes up, Y goes down)  
- **r = 0.0**: No relationship at all

> 💡 **Important warning:** Correlation ≠ Causation!
> Ice cream sales and drowning rates are correlated — but ice cream doesn't cause drowning.
> Both increase in summer. Always think critically about WHY two things correlate.
""",
            "skewness": """
### 📐 Understanding Skewness
**Skewness** tells you if your data is symmetrical or lopsided.

```
Negative skew: most values high, few very low  ← tail on left
Normal:        bell curve, balanced around mean
Positive skew: most values low, few very high  → tail on right
```

> 💡 **Why it matters for ML:** Many machine learning models assume your data 
> is roughly normally distributed. Highly skewed data can make models less accurate.
> The fix is often a **log transformation**: new_value = log(original_value)
"""
        },
        "visualisation": {
            "intro": """
## 📈 Step 3: Data Visualisation

### Why do we visualise data?
Numbers alone are hard to understand. Charts reveal patterns instantly.

> 💡 **Famous example:** Anscombe's Quartet — four datasets with identical 
> statistics (same mean, variance, correlation) but completely different shapes 
> when plotted. You'd never spot the difference from numbers alone!

### Chart Types DataForge Creates:
""",
            "histogram": """
### 📊 Histogram
**What it shows:** How values are distributed — where most of the data clusters

**How to read it:**
- Tall bars = many values in that range
- Short bars = few values in that range  
- Symmetric shape = balanced data
- Long tail to one side = skewed data

**Real-world use:** Understanding age distribution of customers
""",
            "heatmap": """
### 🌡️ Correlation Heatmap
**What it shows:** Relationships between ALL numeric columns at once

**How to read it:**
- 🟢 **Green/Teal** = positive correlation (columns increase together)
- 🔴 **Red** = negative correlation (one increases as other decreases)
- **White** = no correlation
- The darker the colour, the stronger the relationship

**Real-world use:** Finding which factors are related to customer churn
""",
            "boxplot": """
### 📦 Box Plot
**What it shows:** Distribution, spread, and outliers in one chart

**How to read it:**
```
     ─── ← Maximum (excluding outliers)
     │
  ┌──┴──┐
  │     │  ← Upper quartile (Q3) — top 25%
  │─────│  ← Median (middle value)
  │     │  ← Lower quartile (Q1) — bottom 25%
  └──┬──┘
     │
     ─── ← Minimum (excluding outliers)
     ●   ← Outlier points
```
**Real-world use:** Comparing salary ranges across departments
""",
            "scatter": """
### 🔵 Scatter Plot
**What it shows:** The relationship between two specific columns

**How to read it:**
- Points going up-right = positive correlation
- Points going down-right = negative correlation
- Random scatter = no relationship
- The trend line shows the overall direction

**Real-world use:** Does spending more on advertising increase sales?
"""
        },
        "automl": {
            "intro": """
## 🤖 Step 4: Machine Learning

### What is Machine Learning?
Machine learning is teaching a computer to make predictions from data — 
without explicitly programming every rule.

> 💡 **Analogy:** Instead of telling a computer "if age > 65 and cholesterol > 200, 
> flag as high risk", you show it thousands of patient records and let it 
> **learn the patterns itself**.

### Two Types of ML Problems:

**Classification** — predicting a category
- Will this customer churn? (Yes/No)
- Is this email spam? (Spam/Not spam)
- What species is this flower? (Rose/Tulip/Daisy)

**Regression** — predicting a number
- What will this house sell for? (£245,000)
- How many units will we sell next month? (1,247)
- What will a patient's blood pressure be? (135)

DataForge automatically detects which type your problem is!
""",
            "models": {
                "Logistic Regression": """
**Logistic Regression** is the simplest classification algorithm.
- Draws a straight line to separate categories
- Very interpretable — you can see exactly what it learned
- Works best when the relationship is roughly linear
- ✅ Great starting point, very fast to train
""",
                "Random Forest": """
**Random Forest** builds many decision trees and combines their votes.
- Like asking 100 experts and taking the majority opinion
- Handles complex non-linear patterns well
- Resistant to overfitting (memorising training data)
- ✅ One of the most reliable all-round algorithms
""",
                "Decision Tree": """
**Decision Tree** makes predictions by asking a series of yes/no questions.
- Very easy to understand and visualise
- Like a flowchart of decisions
- Can overfit (memorise training data) if too deep
- ✅ Great for understanding what factors matter most
""",
                "Gradient Boosting": """
**Gradient Boosting** builds trees sequentially, each one fixing the mistakes of the last.
- Often the highest accuracy algorithm
- Powers many Kaggle competition winners
- Takes longer to train
- ✅ Best choice when accuracy is the priority
""",
                "Linear Regression": """
**Linear Regression** fits a straight line through your data points.
- The simplest regression algorithm
- Equation: y = mx + c (like school maths!)
- Assumes a linear relationship
- ✅ Start here — if it works well, no need for complexity
""",
                "K-Nearest Neighbors": """
**K-Nearest Neighbors (KNN)** classifies by looking at the closest data points.
- Like asking your nearest neighbours for their opinion
- No training phase — just memorises the data
- Slows down with large datasets
- ✅ Intuitive and works well for smaller datasets
"""
            },
            "metrics": """
### 📏 How do we measure model performance?

**For Classification:**
- **Accuracy** = (Correct predictions) / (Total predictions)
- 90% accuracy means the model gets 9 out of 10 predictions right
- ⚠️ Warning: 90% accuracy sounds great — but if 90% of emails are not spam, 
  a model that always says "not spam" gets 90% accuracy without learning anything!

**For Regression:**
- **R² Score** = How much of the variation the model explains
- R² = 1.0 is perfect, R² = 0.0 means the model learned nothing
- R² = 0.85 means the model explains 85% of the variation in the target

**Cross-Validation:**
DataForge uses **3-fold cross-validation** — it trains and tests the model 3 times 
on different portions of the data to get a more reliable performance estimate.
"""
        }
    },

    "intermediate": {
        "intro": """
## 👋 Welcome to DataForge — Data Science Pipeline Tutor

This session will walk you through a complete end-to-end data science workflow:
**Ingestion → Cleaning → EDA → Visualisation → Modelling → Evaluation**

Each step includes technical explanations of the methods used, the statistical 
rationale behind each decision, and code snippets showing how it works under the hood.

Let's begin with your dataset. 🚀
""",
        "cleaning": {
            "intro": """
## 🧹 Step 1: Data Preprocessing

DataForge applies the following preprocessing pipeline:

```python
# 1. Standardise column names
df.columns = df.columns.str.strip().str.replace(" ", "_").str.lower()

# 2. Remove duplicates
df = df.drop_duplicates()

# 3. Imputation strategy
for col in numeric_cols:
    df[col].fillna(df[col].median(), inplace=True)  # Median: robust to outliers
for col in categorical_cols:
    df[col].fillna(df[col].mode()[0], inplace=True)

# 4. Outlier detection (IQR method)
Q1, Q3 = df[col].quantile([0.25, 0.75])
IQR = Q3 - Q1
outliers = df[(df[col] < Q1 - 1.5*IQR) | (df[col] > Q3 + 1.5*IQR)]
```

**Why median imputation?** Median is resistant to outliers (breakdown point = 0.5), 
unlike mean (breakdown point ≈ 0). For skewed distributions, median better represents 
the central tendency.

**Why flag outliers rather than remove?** Outlier removal is domain-dependent. 
In fraud detection, outliers are signal not noise. The IQR method (Tukey fences) 
has a false positive rate of ~0.7% for normal distributions.
""",
            "missing_values": """
### Missing Data Mechanisms (Little & Rubin, 1987)

Understanding **why** data is missing is critical before choosing an imputation strategy:

| Mechanism | Description | Implication |
|---|---|---|
| **MCAR** | Missing Completely At Random | Safe to delete or impute |
| **MAR** | Missing At Random (depends on observed data) | Multiple imputation preferred |
| **MNAR** | Missing Not At Random | Requires domain knowledge |

DataForge uses **single imputation** (median/mode) — appropriate for MCAR/MAR 
with low missingness. For high missingness (>20%), consider **multiple imputation** 
using `sklearn.impute.IterativeImputer`.
""",
            "outliers": """
### Outlier Detection Methods

DataForge uses the **Tukey IQR method**:
```python
lower_fence = Q1 - 1.5 * IQR
upper_fence = Q3 + 1.5 * IQR
```

Alternative methods for comparison:
- **Z-score method**: flag if |z| > 3 — sensitive to non-normal distributions
- **Isolation Forest**: unsupervised ML approach, better for multivariate outliers
- **DBSCAN**: density-based, identifies outliers as noise points

The IQR method is distribution-free (non-parametric) — no normality assumption required.
"""
        },
        "analysis": {
            "intro": """
## 📊 Step 2: Exploratory Data Analysis (EDA)

EDA (coined by John Tukey, 1977) is the process of summarising and visualising 
data to discover patterns, anomalies, and relationships before formal modelling.

**Key statistics computed:**

```python
# Descriptive statistics
df.describe()  # count, mean, std, min, 25%, 50%, 75%, max

# Pearson correlation coefficient
r = df[col_a].corr(df[col_b])
# r = Σ((xi - x̄)(yi - ȳ)) / √(Σ(xi-x̄)² × Σ(yi-ȳ)²)

# Skewness (Fisher's moment coefficient)
skew = df[col].skew()
# Positive: right tail; Negative: left tail; |skew| > 1: significant
```
""",
            "skewness": """
### Skewness & Transformations

For **positively skewed** data (right tail), common transformations:
```python
import numpy as np
df[col] = np.log1p(df[col])      # Log transform (log(x+1))
df[col] = np.sqrt(df[col])        # Square root transform
df[col] = df[col] ** (1/3)        # Cube root transform
```

For **negatively skewed** data (left tail):
```python
df[col] = df[col] ** 2            # Square transform
df[col] = np.exp(df[col])         # Exponential transform
```

**Box-Cox transformation** (optimal power transformation):
```python
from scipy.stats import boxcox
df[col], lambda_ = boxcox(df[col] + 1)  # +1 to handle zeros
```
"""
        },
        "visualisation": {
            "intro": """
## 📈 Step 3: Data Visualisation

DataForge generates visualisations following Tufte's principles of data-ink ratio — 
maximising the data:ink ratio and eliminating chartjunk.

Charts generated and their statistical basis:
""",
            "histogram": """
### Histogram
Estimates the **probability density function** of a continuous variable.
```python
# Optimal bin count — Sturges' rule
k = ceil(log2(n) + 1)

# Or Scott's rule (better for non-normal)
h = 3.49 * std * n**(-1/3)
```
Interpretation: shape reveals distribution family (normal, exponential, bimodal, etc.)
""",
            "heatmap": """
### Correlation Heatmap
Visualises the **Pearson correlation matrix** — a symmetric p×p matrix where each 
element r_ij ∈ [-1, 1].

```python
corr_matrix = df[numeric_cols].corr(method='pearson')
# method options: 'pearson', 'spearman' (rank-based), 'kendall' (concordance)
```

**Spearman** correlation is more robust for non-normal distributions or ordinal data.
""",
            "boxplot": """
### Box Plot (Tukey, 1977)
Displays the **five-number summary**: min, Q1, median, Q3, max

```python
# Whisker extent: 1.5 × IQR (Tukey's default)
# Points beyond whiskers plotted individually as potential outliers
```

Useful for: comparing distributions, detecting skewness, identifying outliers
""",
            "scatter": """
### Scatter Plot with OLS Trendline
```python
# Ordinary Least Squares regression line
# β = (XᵀX)⁻¹Xᵀy
# Minimises sum of squared residuals

import statsmodels.api as sm
X = sm.add_constant(df[col_a])
model = sm.OLS(df[col_b], X).fit()
# model.params: intercept and slope
# model.rsquared: proportion of variance explained
```
"""
        },
        "automl": {
            "intro": """
## 🤖 Step 4: Automated Machine Learning

DataForge implements a lightweight AutoML pipeline:

```python
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler

# 80/20 train-test split with stratification
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y  # stratify for classification
)

# Feature scaling — critical for distance-based models (KNN, SVM, Logistic Regression)
scaler = StandardScaler()  # z-score normalisation: (x - μ) / σ
X_scaled = scaler.fit_transform(X_train)
```

**Why standardise?** Features on different scales (e.g., age in [18,90] vs income 
in [0, 500000]) cause gradient descent algorithms and distance metrics to be dominated 
by the larger-scale feature.
""",
            "models": {
                "Logistic Regression": """
**Logistic Regression** applies the sigmoid function to a linear combination of features:
```python
P(y=1) = 1 / (1 + e^(-z))  where z = β₀ + β₁x₁ + β₂x₂ + ...
# Optimised via maximum likelihood estimation
# Regularisation: L1 (Lasso) or L2 (Ridge) via C parameter
```
Decision boundary is linear in feature space. Interpretable coefficients (log-odds).
""",
                "Random Forest": """
**Random Forest** — ensemble of decision trees via bagging + feature randomness:
```python
# Each tree trained on bootstrap sample (with replacement)
# At each split: consider only sqrt(n_features) random features
# Final prediction: majority vote (classification) or mean (regression)
# Out-of-bag (OOB) error: free cross-validation estimate
```
Reduces variance without increasing bias. Feature importance = mean impurity decrease.
""",
                "Gradient Boosting": """
**Gradient Boosting** — additive model trained via functional gradient descent:
```python
F_m(x) = F_{m-1}(x) + η × h_m(x)
# η = learning rate (shrinkage)
# h_m = weak learner fitted to negative gradient of loss function
# For classification: log loss; for regression: MSE
```
More prone to overfitting than Random Forest. Tune: n_estimators, learning_rate, max_depth.
""",
                "Decision Tree": """
**Decision Tree** — recursive binary partitioning of feature space:
```python
# Split criterion (classification): Gini impurity or Information Gain (entropy)
# Gini(t) = 1 - Σ p_i²
# Entropy(t) = -Σ p_i log₂(p_i)
# Split criterion (regression): MSE reduction
```
Prone to overfitting — control with max_depth, min_samples_split, min_samples_leaf.
""",
                "Linear Regression": """
**Linear Regression** — OLS estimation of β in y = Xβ + ε:
```python
β = (XᵀX)⁻¹Xᵀy  # Normal equation (closed form)
# Assumptions: linearity, independence, homoscedasticity, normality of residuals
# Evaluate: R², adjusted R², F-statistic, residual plots
```
Ridge (L2): β_ridge = (XᵀX + λI)⁻¹Xᵀy — handles multicollinearity.
""",
                "K-Nearest Neighbors": """
**KNN** — non-parametric, instance-based learning:
```python
# Classification: majority vote among k nearest neighbours
# Regression: mean of k nearest neighbours
# Distance metric: Euclidean (default), Manhattan, Minkowski
# Optimal k: cross-validate; odd k to avoid ties
```
Time complexity O(nd) per query — slow for large datasets. No training phase.
"""
            },
            "metrics": """
### Model Evaluation Metrics

**Classification:**
```python
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score

accuracy = (TP + TN) / (TP + TN + FP + FN)
precision = TP / (TP + FP)   # Of predicted positives, how many are correct?
recall = TP / (TP + FN)       # Of actual positives, how many did we catch?
f1 = 2 * (precision * recall) / (precision + recall)  # Harmonic mean
```

**Regression:**
```python
R² = 1 - SS_res/SS_tot  # Proportion of variance explained
RMSE = sqrt(mean((y_pred - y_true)²))  # In same units as target
MAE = mean(|y_pred - y_true|)          # Robust to outliers
```

**Cross-Validation:**
```python
cv_scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
# 5-fold: train on 80%, test on 20%, repeat 5 times
# Reduces variance of performance estimate vs single train/test split
```
"""
        }
    }
}


def get_lesson(stage: str, substage: str = "intro", level: str = "beginner",
               context: dict = None) -> str:
    """
    Returns the lesson text for a given stage and level.
    context can include actual data findings to make lessons personalised.
    """
    try:
        lesson = LESSONS[level][stage]
        if substage == "intro":
            text = lesson.get("intro", "") if isinstance(lesson, dict) else lesson
        else:
            text = lesson.get(substage, "") if isinstance(lesson, dict) else ""

        # Personalise with actual data findings
        if context and text:
            if "n_duplicates" in context and context["n_duplicates"] > 0:
                text = text.replace(
                    "DataForge removes them automatically",
                    f"DataForge found and removed **{context['n_duplicates']:,} duplicate rows** in your dataset"
                )
            if "missing_count" in context and context["missing_count"] > 0:
                text += f"\n\n> 📊 **In your dataset:** {context['missing_count']:,} missing values were found and imputed."
            if "best_model" in context:
                text += f"\n\n> 🏆 **In your dataset:** DataForge selected **{context['best_model']}** as the best model."

        return text or f"*Lesson content for {stage}/{substage} at {level} level.*"

    except KeyError:
        return f"*Lesson content for {stage}/{substage} at {level} level.*"


def get_model_explanation(model_name: str, level: str = "beginner") -> str:
    """Returns explanation of a specific ML model."""
    try:
        return LESSONS[level]["automl"]["models"].get(
            model_name,
            f"**{model_name}** is a machine learning algorithm used for prediction tasks."
        )
    except KeyError:
        return f"**{model_name}** — explanation not available."


def generate_quiz(stage: str, level: str = "beginner", findings: dict = None) -> list:
    """Generate quiz questions for a given stage."""
    quizzes = {
        "cleaning": [
            {
                "q": "Why do we use the **median** to fill missing values instead of the **mean**?",
                "options": [
                    "Because median is always larger than mean",
                    "Because median is resistant to outliers and skewed data",
                    "Because mean is harder to calculate",
                    "Because median works for text columns too"
                ],
                "answer": 1,
                "explanation": "The median is the middle value when sorted — it's not affected by extreme values. If one person earns £10M, the mean salary skyrockets but the median barely changes."
            },
            {
                "q": "DataForge **flags** outliers but doesn't delete them. Why?",
                "options": [
                    "Because deleting is too slow",
                    "Because outliers are always errors",
                    "Because outliers may be the most important data points (e.g. fraud)",
                    "Because the IQR method is inaccurate"
                ],
                "answer": 2,
                "explanation": "In fraud detection, the unusual transaction IS the fraud. Removing outliers blindly could delete your most valuable signal!"
            },
        ],
        "analysis": [
            {
                "q": "Two columns have a correlation of r = 0.85. What does this mean?",
                "options": [
                    "One column causes the other to increase",
                    "They have a strong positive relationship — as one goes up, the other tends to go up",
                    "They are perfectly related",
                    "The analysis has an 85% accuracy"
                ],
                "answer": 1,
                "explanation": "Correlation measures the strength of a linear relationship. r=0.85 is strong and positive, but remember: correlation ≠ causation!"
            },
            {
                "q": "A column has a skewness of +2.5. What should you consider doing?",
                "options": [
                    "Delete the column",
                    "Apply a log transformation to make it more normal",
                    "Replace all values with the mean",
                    "Nothing — skewness doesn't matter"
                ],
                "answer": 1,
                "explanation": "High positive skewness means a long right tail. A log transformation compresses large values and stretches small ones, making the distribution more symmetric."
            },
        ],
        "visualisation": [
            {
                "q": "In a box plot, what does the line in the **middle of the box** represent?",
                "options": ["The mean", "The median", "The mode", "The standard deviation"],
                "answer": 1,
                "explanation": "The middle line is the median (50th percentile). The box spans Q1 to Q3, showing the middle 50% of the data."
            },
            {
                "q": "In a correlation heatmap, a **dark red** cell between columns A and B means:",
                "options": [
                    "A and B are strongly positively correlated",
                    "A and B are strongly negatively correlated",
                    "A and B have no relationship",
                    "There is an error in the data"
                ],
                "answer": 1,
                "explanation": "Red indicates negative correlation — as one variable increases, the other decreases. Dark = strong."
            },
        ],
        "automl": [
            {
                "q": "What is **cross-validation** used for?",
                "options": [
                    "Making the model train faster",
                    "Getting a more reliable estimate of model performance",
                    "Cleaning the data before training",
                    "Selecting which columns to use"
                ],
                "answer": 1,
                "explanation": "Cross-validation trains and tests the model multiple times on different subsets of data, giving a more stable performance estimate than a single train/test split."
            },
            {
                "q": "A model achieves 95% accuracy on training data but only 60% on test data. This is called:",
                "options": [
                    "Underfitting",
                    "Overfitting",
                    "Cross-validation",
                    "Feature importance"
                ],
                "answer": 1,
                "explanation": "Overfitting means the model memorised the training data instead of learning general patterns. It performs poorly on new, unseen data."
            },
        ]
    }

    questions = quizzes.get(stage, [])
    if level == "intermediate":
        # Add harder versions
        harder = {
            "cleaning": [{
                "q": "Which missing data mechanism makes deletion/imputation potentially biased?",
                "options": ["MCAR", "MAR", "MNAR", "All of the above"],
                "answer": 2,
                "explanation": "MNAR (Missing Not At Random) means the probability of missing depends on the missing value itself — e.g., high earners skip income questions. Simple imputation introduces bias."
            }],
            "analysis": [{
                "q": "Pearson correlation assumes which of the following?",
                "options": [
                    "Both variables are binary",
                    "Both variables are normally distributed and linearly related",
                    "The dataset has no missing values",
                    "The sample size is greater than 1000"
                ],
                "answer": 1,
                "explanation": "Pearson measures linear correlation and is parametric. For non-normal distributions or ordinal data, use Spearman's rank correlation instead."
            }],
        }
        questions = questions + harder.get(stage, [])

    return questions