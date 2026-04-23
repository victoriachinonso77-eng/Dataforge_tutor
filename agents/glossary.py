# agents/glossary.py — Data Science Glossary Tab
# A searchable dictionary of data science terms for students

import streamlit as st

GLOSSARY = {
    "A": [
        {"term": "Accuracy", "definition": "The proportion of correct predictions out of all predictions made by a model. Calculated as (TP + TN) / Total. Can be misleading on imbalanced datasets."},
        {"term": "Algorithm", "definition": "A set of rules or instructions a computer follows to solve a problem or make a decision, such as a decision tree or neural network."},
        {"term": "Anomaly Detection", "definition": "The process of identifying data points that deviate significantly from the rest of the dataset. Used in fraud detection and quality control."},
        {"term": "AutoML", "definition": "Automated Machine Learning — tools and techniques that automate the process of selecting and tuning ML models, making it easier for non-experts to build models."},
    ],
    "B": [
        {"term": "Bias (Statistical)", "definition": "A systematic error in a model or dataset that causes consistently incorrect predictions. Can arise from unrepresentative training data."},
        {"term": "Binary Classification", "definition": "A machine learning task where the model predicts one of exactly two possible outcomes, such as spam/not spam or pass/fail."},
        {"term": "Boxplot", "definition": "A chart that displays the distribution of a dataset through its quartiles, showing the median, spread, and any outliers."},
    ],
    "C": [
        {"term": "Classification", "definition": "A supervised learning task where the model predicts which category a data point belongs to, such as classifying emails as spam or not spam."},
        {"term": "Clustering", "definition": "An unsupervised learning technique that groups similar data points together without using labelled data. K-means is a common clustering algorithm."},
        {"term": "Confusion Matrix", "definition": "A table showing the counts of true positives, true negatives, false positives, and false negatives for a classification model's predictions."},
        {"term": "Correlation", "definition": "A statistical measure of how strongly two variables are related. Values range from -1 (perfect negative) to +1 (perfect positive), with 0 meaning no relationship."},
        {"term": "Cross-Validation", "definition": "A technique for evaluating a model by splitting data into multiple folds and training/testing on different combinations to get a reliable performance estimate."},
        {"term": "CSV", "definition": "Comma-Separated Values — a plain text file format for storing tabular data, where each row is a line and columns are separated by commas."},
    ],
    "D": [
        {"term": "Data Cleaning", "definition": "The process of identifying and fixing errors, inconsistencies, and missing values in a dataset before analysis or modelling."},
        {"term": "Data Leakage", "definition": "When information from outside the training dataset is used to train a model, causing it to perform unrealistically well on test data but fail in the real world."},
        {"term": "DataFrame", "definition": "A two-dimensional data structure (like a table) used in Pandas, with rows and columns, commonly used for data manipulation in Python."},
        {"term": "Decision Tree", "definition": "A tree-shaped model that makes predictions by splitting data based on feature values at each node, ending in a predicted output at the leaves."},
        {"term": "Deep Learning", "definition": "A subset of machine learning using neural networks with many layers (hence 'deep') to learn complex patterns, particularly in images, text, and audio."},
        {"term": "Distribution", "definition": "The pattern of how values are spread across a dataset. Common distributions include normal (bell curve), skewed, and uniform distributions."},
        {"term": "Duplicate", "definition": "A row in a dataset that is identical (or nearly identical) to another row, which can distort analysis and should typically be removed during data cleaning."},
    ],
    "E": [
        {"term": "Ensemble Method", "definition": "A technique that combines multiple models to produce a better prediction than any individual model alone. Random Forest is a popular ensemble method."},
        {"term": "Epoch", "definition": "One complete pass through the entire training dataset during the training of a neural network or deep learning model."},
        {"term": "EU AI Act", "definition": "European Union legislation regulating AI systems based on their risk level, requiring transparency, documentation, and human oversight for high-risk applications."},
    ],
    "F": [
        {"term": "F1 Score", "definition": "A metric that balances precision and recall into a single score, calculated as 2 × (Precision × Recall) / (Precision + Recall). Useful for imbalanced datasets."},
        {"term": "False Negative (FN)", "definition": "When a model incorrectly predicts the negative class for a data point that is actually positive. Also called a Type II error."},
        {"term": "False Positive (FP)", "definition": "When a model incorrectly predicts the positive class for a data point that is actually negative. Also called a Type I error."},
        {"term": "Feature", "definition": "An individual measurable property or column used as input to a machine learning model. Also called a variable, attribute, or predictor."},
        {"term": "Feature Engineering", "definition": "The process of creating new features or transforming existing ones to improve a model's performance."},
    ],
    "G": [
        {"term": "GPT", "definition": "Generative Pre-trained Transformer — a type of large language model developed by OpenAI, capable of generating human-like text and answering questions."},
        {"term": "Gradient Descent", "definition": "An optimisation algorithm used to minimise a model's error by iteratively adjusting its parameters in the direction that reduces the loss function."},
    ],
    "H": [
        {"term": "Heatmap", "definition": "A colour-coded grid visualisation used to show the magnitude of values in a matrix, commonly used to display correlation between features."},
        {"term": "Hyperparameter", "definition": "A parameter set before training a model (not learned from the data), such as the number of trees in a Random Forest or the learning rate."},
        {"term": "Hypothesis", "definition": "A testable statement about a relationship or pattern in data that statistical analysis is used to support or reject."},
    ],
    "I": [
        {"term": "Imputation", "definition": "The process of filling in missing values in a dataset using a strategy such as the mean, median, or a predicted value."},
        {"term": "Imbalanced Dataset", "definition": "A dataset where one class has significantly more examples than another, which can cause a model to be biased towards the majority class."},
    ],
    "K": [
        {"term": "K-Means", "definition": "A clustering algorithm that partitions data into K groups by minimising the distance between data points and their cluster centre (centroid)."},
        {"term": "K-Nearest Neighbours (KNN)", "definition": "A classification algorithm that assigns a label to a data point based on the majority label of its K nearest neighbours in the feature space."},
        {"term": "Kaggle", "definition": "An online platform for data science competitions and datasets, widely used for learning and practising machine learning with real-world data."},
    ],
    "L": [
        {"term": "Label", "definition": "The target output value in a supervised learning dataset — what the model is trying to predict, such as 'spam' or 'not spam'."},
        {"term": "Linear Regression", "definition": "A model that predicts a continuous numeric output by fitting a straight line through the data, minimising the sum of squared errors."},
        {"term": "Logistic Regression", "definition": "Despite the name, a classification algorithm (not regression) that predicts the probability of a binary outcome using a sigmoid function."},
        {"term": "Loss Function", "definition": "A function that measures how far a model's predictions are from the true values. The model is trained by minimising this function."},
    ],
    "M": [
        {"term": "Machine Learning (ML)", "definition": "A branch of AI where systems learn patterns from data and improve their performance on tasks without being explicitly programmed."},
        {"term": "Mean", "definition": "The average of a set of values, calculated by summing all values and dividing by the count. Sensitive to outliers."},
        {"term": "Median", "definition": "The middle value of a sorted dataset. More robust to outliers than the mean and better represents the centre of skewed data."},
        {"term": "Missing Values", "definition": "Data points that are absent from a dataset, represented as NaN or null. Must be handled before modelling, typically by removal or imputation."},
        {"term": "Model", "definition": "A mathematical representation of a pattern in data, trained on examples and used to make predictions or decisions on new, unseen data."},
        {"term": "Multicollinearity", "definition": "When two or more features in a dataset are highly correlated with each other, which can make it difficult to determine their individual effects on the target."},
    ],
    "N": [
        {"term": "Naive Bayes", "definition": "A probabilistic classifier based on Bayes' theorem that assumes all features are independent of each other. Fast and effective for text classification."},
        {"term": "Normalisation", "definition": "Scaling numerical features to a standard range (usually 0 to 1) so that no single feature dominates due to its scale."},
        {"term": "Null Value", "definition": "A missing or undefined value in a dataset, often represented as NaN (Not a Number) in Python's Pandas library."},
    ],
    "O": [
        {"term": "Outlier", "definition": "A data point that lies far from the rest of the data. Outliers can indicate errors in data collection or genuinely unusual observations."},
        {"term": "Overfitting", "definition": "When a model learns the training data too well, including its noise, and performs poorly on new unseen data. Prevented by regularisation and cross-validation."},
    ],
    "P": [
        {"term": "Pandas", "definition": "A Python library for data manipulation and analysis, providing DataFrame and Series structures for working with tabular and time series data."},
        {"term": "Precision", "definition": "The proportion of positive predictions that were actually correct. Calculated as TP / (TP + FP). Important when false positives are costly."},
        {"term": "Proxy Variable", "definition": "A variable that is correlated with a protected attribute (such as race or gender) and can introduce bias into a model even when the protected attribute is excluded."},
    ],
    "R": [
        {"term": "Random Forest", "definition": "An ensemble model that builds many decision trees on random subsets of data and features, then combines their predictions by voting or averaging."},
        {"term": "Recall", "definition": "The proportion of actual positives that were correctly identified by the model. Calculated as TP / (TP + FN). Important when false negatives are costly."},
        {"term": "Regression", "definition": "A supervised learning task where the model predicts a continuous numeric output, such as predicting house prices or temperature."},
        {"term": "ROC-AUC", "definition": "Receiver Operating Characteristic — Area Under Curve. A metric measuring a model's ability to distinguish between classes across all classification thresholds."},
    ],
    "S": [
        {"term": "Scikit-learn", "definition": "A Python machine learning library providing tools for classification, regression, clustering, and preprocessing, built on NumPy and SciPy."},
        {"term": "Skewness", "definition": "A measure of the asymmetry of a data distribution. Positive skew means a long right tail; negative skew means a long left tail."},
        {"term": "Standard Deviation", "definition": "A measure of how spread out values are around the mean. A high standard deviation means values are widely dispersed."},
        {"term": "Supervised Learning", "definition": "A type of machine learning where the model is trained on labelled data — input-output pairs — and learns to predict the output for new inputs."},
        {"term": "Support Vector Machine (SVM)", "definition": "A classification algorithm that finds the optimal boundary (hyperplane) between classes by maximising the margin between the nearest data points."},
    ],
    "T": [
        {"term": "Target Variable", "definition": "The column in a dataset that a model is trained to predict. Also called the dependent variable, label, or output."},
        {"term": "Test Set", "definition": "A portion of the dataset kept separate from training, used to evaluate how well the model generalises to unseen data."},
        {"term": "Training Set", "definition": "The portion of data used to train a machine learning model. The model learns patterns from this data."},
        {"term": "Transfer Learning", "definition": "Using a model trained on one task as a starting point for a different but related task, reducing the need for large amounts of new training data."},
    ],
    "U": [
        {"term": "Underfitting", "definition": "When a model is too simple to capture the patterns in the data, resulting in poor performance on both training and test data."},
        {"term": "Unsupervised Learning", "definition": "A type of machine learning where the model finds patterns in data without labelled examples, such as clustering or dimensionality reduction."},
    ],
    "V": [
        {"term": "Validation Set", "definition": "A subset of data used during training to tune hyperparameters and evaluate model performance, separate from both training and test sets."},
        {"term": "Variance", "definition": "A measure of how much a model's predictions change when trained on different subsets of data. High variance leads to overfitting."},
        {"term": "Visualisation", "definition": "The representation of data through charts, graphs, and plots to help identify patterns, trends, and outliers that are not obvious in raw numbers."},
    ],
    "W": [
        {"term": "Weight", "definition": "A learnable parameter in a machine learning model that is adjusted during training to minimise the loss function."},
    ],
}


def show_glossary_tab(st) -> None:
    """Renders the full searchable glossary tab."""
    st.header("📖 Data Science Glossary")
    st.markdown("Search for any data science term used in DataForge or your studies.")

    # Search bar
    query = st.text_input("🔍 Search a term...", placeholder="e.g. overfitting, precision, clustering")

    if query.strip():
        _show_search_results(st, query.strip().lower())
    else:
        _show_full_glossary(st)


def _show_search_results(st, query: str) -> None:
    matches = []
    for letter, terms in GLOSSARY.items():
        for entry in terms:
            if query in entry["term"].lower() or query in entry["definition"].lower():
                matches.append(entry)

    if not matches:
        st.warning(f"No results found for '{query}'. Try a different keyword.")
        return

    st.success(f"Found {len(matches)} result(s) for '{query}':")
    for entry in matches:
        with st.expander(f"**{entry['term']}**", expanded=True):
            st.markdown(entry["definition"])


def _show_full_glossary(st) -> None:
    st.markdown(f"**{sum(len(v) for v in GLOSSARY.values())} terms across {len(GLOSSARY)} letters**")
    st.divider()

    for letter, terms in sorted(GLOSSARY.items()):
        st.markdown(f"### {letter}")
        for entry in terms:
            with st.expander(f"{entry['term']}"):
                st.markdown(entry["definition"])
