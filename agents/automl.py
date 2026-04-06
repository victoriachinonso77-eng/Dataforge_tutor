# agents/automl.py
# Agent 5 — Automatic Machine Learning Model Selection & Training

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import (accuracy_score, r2_score, mean_squared_error,
                              classification_report, confusion_matrix)
from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge
from sklearn.ensemble import (RandomForestClassifier, RandomForestRegressor,
                               GradientBoostingClassifier, GradientBoostingRegressor)
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.svm import SVC, SVR
from sklearn.neighbors import KNeighborsClassifier
import warnings
warnings.filterwarnings("ignore")


def detect_task_type(df: pd.DataFrame, target_col: str) -> str:
    """Detect whether this is a classification or regression problem."""
    target = df[target_col].dropna()
    n_unique = target.nunique()
    dtype = target.dtype

    if dtype == object or n_unique <= 10:
        return "classification"
    elif n_unique / len(target) < 0.05:
        return "classification"
    else:
        return "regression"


def prepare_features(df: pd.DataFrame, target_col: str):
    """Prepare X and y for ML, handling categorical columns."""
    df_clean = df.copy().dropna()

    # Separate target
    y = df_clean[target_col]
    X = df_clean.drop(columns=[target_col])

    # Drop non-numeric columns that can't be encoded easily
    X = X.select_dtypes(include=[np.number])

    # Encode target if categorical
    le = None
    if y.dtype == object or y.dtype.name == "category":
        le = LabelEncoder()
        y = le.fit_transform(y)
    else:
        y = y.values

    return X, y, le, list(X.columns)


def run_automl(df: pd.DataFrame, target_col: str) -> dict:
    """
    Automatically selects the best ML model for the given target column.
    Returns results dict with model comparisons and best model metrics.
    """
    results = {
        "target_col": target_col,
        "task_type": None,
        "models": [],
        "best_model": None,
        "best_score": None,
        "best_metric": None,
        "feature_importance": {},
        "classification_report": None,
        "error": None,
        "n_samples": len(df),
        "n_features": 0,
    }

    try:
        # Detect task
        task = detect_task_type(df, target_col)
        results["task_type"] = task

        # Prepare data
        X, y, le, feature_names = prepare_features(df, target_col)
        results["n_features"] = len(feature_names)

        if len(X) < 20:
            results["error"] = "Not enough samples for ML (need at least 20 rows)"
            return results

        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )

        # Define models
        if task == "classification":
            models = {
                "Logistic Regression":     LogisticRegression(max_iter=1000, random_state=42),
                "Random Forest":           RandomForestClassifier(n_estimators=100, random_state=42),
                "Decision Tree":           DecisionTreeClassifier(random_state=42),
                "Gradient Boosting":       GradientBoostingClassifier(random_state=42),
                "K-Nearest Neighbors":     KNeighborsClassifier(),
            }
            metric_name = "Accuracy"
        else:
            models = {
                "Linear Regression":       LinearRegression(),
                "Ridge Regression":        Ridge(random_state=42),
                "Random Forest":           RandomForestRegressor(n_estimators=100, random_state=42),
                "Decision Tree":           DecisionTreeRegressor(random_state=42),
                "Gradient Boosting":       GradientBoostingRegressor(random_state=42),
            }
            metric_name = "R² Score"

        results["best_metric"] = metric_name
        best_score = -np.inf
        best_model_name = None
        best_model_obj = None

        # Train and evaluate each model
        for name, model in models.items():
            try:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)

                if task == "classification":
                    score = accuracy_score(y_test, y_pred)
                    cv_scores = cross_val_score(model, X_scaled, y, cv=3, scoring="accuracy")
                else:
                    score = r2_score(y_test, y_pred)
                    cv_scores = cross_val_score(model, X_scaled, y, cv=3, scoring="r2")

                results["models"].append({
                    "name": name,
                    "score": round(float(score), 4),
                    "cv_mean": round(float(cv_scores.mean()), 4),
                    "cv_std": round(float(cv_scores.std()), 4),
                })

                if score > best_score:
                    best_score = score
                    best_model_name = name
                    best_model_obj = model

            except Exception as e:
                results["models"].append({
                    "name": name, "score": 0.0, "cv_mean": 0.0, "cv_std": 0.0,
                    "error": str(e)
                })

        # Sort models by score
        results["models"] = sorted(results["models"], key=lambda x: x["score"], reverse=True)
        results["best_model"] = best_model_name
        results["best_score"] = round(float(best_score), 4)

        # Feature importance for best model
        if best_model_obj and hasattr(best_model_obj, "feature_importances_"):
            importances = best_model_obj.feature_importances_
            fi = sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True)
            results["feature_importance"] = {k: round(float(v), 4) for k, v in fi[:10]}

        # Classification report for best model
        if task == "classification" and best_model_obj:
            best_model_obj.fit(X_train, y_train)
            y_pred_best = best_model_obj.predict(X_test)
            results["classification_report"] = classification_report(
                y_test, y_pred_best, output_dict=True, zero_division=0
            )

    except Exception as e:
        results["error"] = str(e)

    return results