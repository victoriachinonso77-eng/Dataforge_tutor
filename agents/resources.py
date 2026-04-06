# agents/resources.py
# Resource Recommender Agent — Suggests YouTube videos and articles per topic

RESOURCES = {
    "data_science_intro": {
        "beginner": {
            "videos": [
                {
                    "title": "What is Data Science? (Plain English)",
                    "channel": "IBM Technology",
                    "url": "https://www.youtube.com/watch?v=RBSUwFGa6Fk",
                    "duration": "7 min",
                    "why": "Perfect starting point — explains data science without any jargon"
                },
                {
                    "title": "Data Science In 5 Minutes",
                    "channel": "Simplilearn",
                    "url": "https://www.youtube.com/watch?v=X3paOmcrTjQ",
                    "duration": "5 min",
                    "why": "Quick overview of what data scientists actually do day-to-day"
                },
                {
                    "title": "Data Science Full Course for Beginners",
                    "channel": "freeCodeCamp",
                    "url": "https://www.youtube.com/watch?v=ua-CiDNNj30",
                    "duration": "6 hrs",
                    "why": "Comprehensive free course if you want to go deep"
                },
            ],
            "articles": [
                {
                    "title": "What Is Data Science? A Beginner's Guide",
                    "source": "IBM",
                    "url": "https://www.ibm.com/topics/data-science",
                    "why": "Clear, jargon-free introduction from one of the leading tech companies"
                },
                {
                    "title": "Data Science for Beginners",
                    "source": "Towards Data Science",
                    "url": "https://towardsdatascience.com/data-science-for-beginners-5b1e5e6e1e1e",
                    "why": "Written by practitioners for beginners — very readable"
                },
            ]
        },
        "intermediate": {
            "videos": [
                {
                    "title": "The Data Science Process Explained",
                    "channel": "StatQuest",
                    "url": "https://www.youtube.com/watch?v=0NcMlYtnAhk",
                    "duration": "12 min",
                    "why": "StatQuest is the gold standard for clear statistical explanations"
                },
            ],
            "articles": [
                {
                    "title": "CRISP-DM: The Data Science Process Framework",
                    "source": "Towards Data Science",
                    "url": "https://towardsdatascience.com/crisp-dm-methodology-leader-in-data-mining-and-big-data-467efd3d3781",
                    "why": "The industry-standard framework for structuring data science projects"
                },
            ]
        }
    },

    "cleaning": {
        "beginner": {
            "videos": [
                {
                    "title": "Data Cleaning in Python — Full Tutorial",
                    "channel": "Keith Galli",
                    "url": "https://www.youtube.com/watch?v=iYie42M1ZyU",
                    "duration": "18 min",
                    "why": "Hands-on walkthrough of real data cleaning in Python — beginner friendly"
                },
                {
                    "title": "Data Cleaning with Pandas",
                    "channel": "Corey Schafer",
                    "url": "https://www.youtube.com/watch?v=ZyhVh-qRZPA",
                    "duration": "14 min",
                    "why": "Great Pandas tutorial focused on fixing messy data"
                },
                {
                    "title": "Missing Data — What To Do?",
                    "channel": "StatQuest with Josh Starmer",
                    "url": "https://www.youtube.com/watch?v=NGca2fCG3T4",
                    "duration": "8 min",
                    "why": "Clear explanation of why missing data matters and how to handle it"
                },
            ],
            "articles": [
                {
                    "title": "A Complete Guide to Data Cleaning",
                    "source": "Towards Data Science",
                    "url": "https://towardsdatascience.com/the-ultimate-guide-to-data-cleaning-3969843991d4",
                    "why": "Step-by-step guide covering every common data cleaning problem"
                },
                {
                    "title": "Handling Missing Values in Python",
                    "source": "Real Python",
                    "url": "https://realpython.com/python-data-cleaning-numpy-pandas/",
                    "why": "Practical, code-heavy guide from one of the best Python learning sites"
                },
                {
                    "title": "Understanding Outliers",
                    "source": "Statistics How To",
                    "url": "https://www.statisticshowto.com/what-is-an-outlier/",
                    "why": "Plain English explanation of what outliers are and when to remove them"
                },
            ]
        },
        "intermediate": {
            "videos": [
                {
                    "title": "Advanced Data Cleaning Techniques",
                    "channel": "Rob Mulla",
                    "url": "https://www.youtube.com/watch?v=9yl6-HEY7_s",
                    "duration": "22 min",
                    "why": "Goes beyond basics — covers regex, type coercion, and complex imputation"
                },
            ],
            "articles": [
                {
                    "title": "Missing Data Mechanisms: MCAR, MAR, MNAR",
                    "source": "Towards Data Science",
                    "url": "https://towardsdatascience.com/how-to-handle-missing-data-8646b18db0d4",
                    "why": "Deep dive into the statistical theory behind missing data"
                },
                {
                    "title": "Multiple Imputation using sklearn",
                    "source": "scikit-learn docs",
                    "url": "https://scikit-learn.org/stable/modules/impute.html",
                    "why": "Official documentation for advanced imputation strategies"
                },
            ]
        }
    },

    "analysis": {
        "beginner": {
            "videos": [
                {
                    "title": "Statistics - A Full University Course",
                    "channel": "freeCodeCamp",
                    "url": "https://www.youtube.com/watch?v=xxpc-HPKN28",
                    "duration": "8 hrs",
                    "why": "Complete university-level stats course, totally free"
                },
                {
                    "title": "Descriptive Statistics: Mean, Median, Mode",
                    "channel": "Khan Academy",
                    "url": "https://www.youtube.com/watch?v=uhxtUt_-GyM",
                    "duration": "9 min",
                    "why": "Khan Academy is the gold standard for clear maths explanations"
                },
                {
                    "title": "Correlation — Clearly Explained",
                    "channel": "StatQuest",
                    "url": "https://www.youtube.com/watch?v=xZ_z8KWkhXE",
                    "duration": "11 min",
                    "why": "Best explanation of correlation vs causation you'll find"
                },
                {
                    "title": "Standard Deviation — Simply Explained",
                    "channel": "StatQuest",
                    "url": "https://www.youtube.com/watch?v=SzZ6GpcfoQY",
                    "duration": "5 min",
                    "why": "Demystifies standard deviation with clear visual examples"
                },
            ],
            "articles": [
                {
                    "title": "Exploratory Data Analysis (EDA) — A Practical Guide",
                    "source": "Towards Data Science",
                    "url": "https://towardsdatascience.com/exploratory-data-analysis-8fc1cb20fd15",
                    "why": "Covers the full EDA process with Python examples"
                },
                {
                    "title": "Correlation vs Causation — Why It Matters",
                    "source": "Statistics How To",
                    "url": "https://www.statisticshowto.com/probability-and-statistics/correlation-analysis/",
                    "why": "Essential reading — a concept that trips up many beginners"
                },
            ]
        },
        "intermediate": {
            "videos": [
                {
                    "title": "Skewness and Kurtosis",
                    "channel": "StatQuest",
                    "url": "https://www.youtube.com/watch?v=okjYjClSjOg",
                    "duration": "8 min",
                    "why": "Technical explanation of distribution shape metrics"
                },
                {
                    "title": "Pearson vs Spearman Correlation",
                    "channel": "StatQuest",
                    "url": "https://www.youtube.com/watch?v=0a0SsKr-M2A",
                    "duration": "10 min",
                    "why": "Understand when to use which correlation coefficient"
                },
            ],
            "articles": [
                {
                    "title": "EDA with Pandas — Complete Guide",
                    "source": "Real Python",
                    "url": "https://realpython.com/pandas-python-explore-dataset/",
                    "why": "Code-heavy EDA walkthrough using a real dataset"
                },
            ]
        }
    },

    "visualisation": {
        "beginner": {
            "videos": [
                {
                    "title": "Data Visualisation for Beginners",
                    "channel": "Google Data Analytics",
                    "url": "https://www.youtube.com/watch?v=C_z1DFBsOhA",
                    "duration": "10 min",
                    "why": "Perfect introduction to why and how we visualise data"
                },
                {
                    "title": "How to Read a Box Plot",
                    "channel": "StatQuest",
                    "url": "https://www.youtube.com/watch?v=fHLhBnmwUM0",
                    "duration": "8 min",
                    "why": "The clearest explanation of box plots available — with animations"
                },
                {
                    "title": "Histograms — Clearly Explained",
                    "channel": "Khan Academy",
                    "url": "https://www.youtube.com/watch?v=gSEYtAjuZ-Y",
                    "duration": "6 min",
                    "why": "Understand what a histogram actually shows step by step"
                },
                {
                    "title": "How to Create Charts in Python (Plotly)",
                    "channel": "Charming Data",
                    "url": "https://www.youtube.com/watch?v=GGL6U0k8WYA",
                    "duration": "20 min",
                    "why": "Learn to create interactive charts like the ones DataForge made"
                },
            ],
            "articles": [
                {
                    "title": "The Data Visualisation Catalogue",
                    "source": "datavizcatalogue.com",
                    "url": "https://datavizcatalogue.com/",
                    "why": "Browse every chart type with explanations — a must-bookmark resource"
                },
                {
                    "title": "Choosing the Right Chart",
                    "source": "FlowingData",
                    "url": "https://flowingdata.com/chart-types",
                    "why": "Helps you pick the right visualisation for your data type"
                },
                {
                    "title": "Plotly Python Documentation",
                    "source": "Plotly",
                    "url": "https://plotly.com/python/",
                    "why": "Official docs for the interactive charting library DataForge uses"
                },
            ]
        },
        "intermediate": {
            "videos": [
                {
                    "title": "Seaborn Full Tutorial",
                    "channel": "Kimberly Fessel",
                    "url": "https://www.youtube.com/watch?v=6GUZXDef2U0",
                    "duration": "30 min",
                    "why": "Deep dive into Seaborn — the library DataForge uses for heatmaps"
                },
            ],
            "articles": [
                {
                    "title": "Edward Tufte's Principles of Data Visualisation",
                    "source": "Towards Data Science",
                    "url": "https://towardsdatascience.com/7-visualizations-with-python-you-cannot-miss-67a42aea3b7",
                    "why": "Learn the design principles that separate good charts from bad ones"
                },
            ]
        }
    },

    "automl": {
        "beginner": {
            "videos": [
                {
                    "title": "Machine Learning for Everybody",
                    "channel": "freeCodeCamp",
                    "url": "https://www.youtube.com/watch?v=i_LwzRVP7bg",
                    "duration": "3.5 hrs",
                    "why": "The best free ML course for complete beginners — no maths required"
                },
                {
                    "title": "Decision Trees — Clearly Explained",
                    "channel": "StatQuest",
                    "url": "https://www.youtube.com/watch?v=_L39rN6gz7Y",
                    "duration": "18 min",
                    "why": "Visual, intuitive explanation of how decision trees work"
                },
                {
                    "title": "Random Forests — Simply Explained",
                    "channel": "StatQuest",
                    "url": "https://www.youtube.com/watch?v=J4Wdy0Wc_xQ",
                    "duration": "10 min",
                    "why": "Builds perfectly on decision trees — understand why forests beat single trees"
                },
                {
                    "title": "Logistic Regression — Clearly Explained",
                    "channel": "StatQuest",
                    "url": "https://www.youtube.com/watch?v=yIYKR4sgzI8",
                    "duration": "9 min",
                    "why": "The most important classification algorithm explained simply"
                },
                {
                    "title": "What is Cross Validation?",
                    "channel": "StatQuest",
                    "url": "https://www.youtube.com/watch?v=fSytzGwwBVw",
                    "duration": "6 min",
                    "why": "Essential concept for evaluating models reliably"
                },
            ],
            "articles": [
                {
                    "title": "A Beginner's Guide to Machine Learning",
                    "source": "Google Machine Learning Crash Course",
                    "url": "https://developers.google.com/machine-learning/crash-course",
                    "why": "Free, interactive ML course from Google — excellent for beginners"
                },
                {
                    "title": "Scikit-learn: Machine Learning in Python",
                    "source": "scikit-learn.org",
                    "url": "https://scikit-learn.org/stable/tutorial/basic/tutorial.html",
                    "why": "Official tutorial for the library DataForge uses for AutoML"
                },
                {
                    "title": "Overfitting vs Underfitting — With Examples",
                    "source": "Towards Data Science",
                    "url": "https://towardsdatascience.com/overfitting-vs-underfitting-a-complete-example-d05dd7e19765",
                    "why": "The most important concept in ML — clearly explained with visuals"
                },
            ]
        },
        "intermediate": {
            "videos": [
                {
                    "title": "Gradient Boosting — Explained",
                    "channel": "StatQuest",
                    "url": "https://www.youtube.com/watch?v=3CC4N4z3GJc",
                    "duration": "15 min",
                    "why": "Deep dive into the most powerful ML algorithm in DataForge's toolkit"
                },
                {
                    "title": "Hyperparameter Tuning (GridSearchCV)",
                    "channel": "Krish Naik",
                    "url": "https://www.youtube.com/watch?v=HdlDYng8g9s",
                    "duration": "20 min",
                    "why": "Next step after AutoML — learn how to optimise your chosen model"
                },
            ],
            "articles": [
                {
                    "title": "Model Evaluation Metrics — Complete Guide",
                    "source": "Towards Data Science",
                    "url": "https://towardsdatascience.com/metrics-to-evaluate-your-machine-learning-algorithm-f10ba6e38234",
                    "why": "Everything about accuracy, precision, recall, F1, AUC-ROC"
                },
                {
                    "title": "Feature Importance in Machine Learning",
                    "source": "Towards Data Science",
                    "url": "https://towardsdatascience.com/feature-importance-in-machine-learning-f2c392c95e54",
                    "why": "Understand exactly what feature importance means and how it's calculated"
                },
            ]
        }
    },

    "general": {
        "beginner": {
            "videos": [
                {
                    "title": "Python for Data Science Full Course",
                    "channel": "freeCodeCamp",
                    "url": "https://www.youtube.com/watch?v=LHBE6Q9XlzI",
                    "duration": "12 hrs",
                    "why": "Learn Python from scratch with a data science focus — completely free"
                },
                {
                    "title": "Pandas Tutorial — Complete Introduction",
                    "channel": "Corey Schafer",
                    "url": "https://www.youtube.com/watch?v=ZyhVh-qRZPA",
                    "duration": "1 hr",
                    "why": "Best Pandas tutorial for beginners — the library DataForge is built on"
                },
            ],
            "articles": [
                {
                    "title": "Kaggle Learn — Free Micro-Courses",
                    "source": "Kaggle",
                    "url": "https://www.kaggle.com/learn",
                    "why": "Free interactive courses on Python, Pandas, ML and more — with real datasets"
                },
                {
                    "title": "Towards Data Science",
                    "source": "towardsdatascience.com",
                    "url": "https://towardsdatascience.com",
                    "why": "The best blog for data science articles — bookmark this!"
                },
            ]
        },
        "intermediate": {
            "videos": [
                {
                    "title": "Scikit-learn Full Tutorial",
                    "channel": "NeuralNine",
                    "url": "https://www.youtube.com/watch?v=0B5eIE_1vpU",
                    "duration": "2 hrs",
                    "why": "Comprehensive tutorial for the ML library powering DataForge's AutoML"
                },
            ],
            "articles": [
                {
                    "title": "The Elements of Statistical Learning (Free PDF)",
                    "source": "Stanford University",
                    "url": "https://hastie.su.domains/ElemStatLearn/",
                    "why": "The definitive textbook on statistical ML — free from Stanford"
                },
            ]
        }
    }
}


def get_resources(topic: str, level: str = "beginner") -> dict:
    """
    Returns curated videos and articles for a given topic and level.
    Falls back to general resources if topic not found.
    """
    topic_data = RESOURCES.get(topic, RESOURCES.get("general", {}))
    level_data = topic_data.get(level, topic_data.get("beginner", {}))
    return {
        "videos":   level_data.get("videos", []),
        "articles": level_data.get("articles", []),
        "topic":    topic,
        "level":    level
    }


def search_resources(query: str, level: str = "beginner") -> dict:
    """
    Searches across all resources for a given query string.
    Returns matching videos and articles.
    """
    query_lower = query.lower()
    matched_videos = []
    matched_articles = []

    topic_map = {
        "clean": "cleaning", "missing": "cleaning", "duplicate": "cleaning",
        "outlier": "cleaning", "null": "cleaning", "impute": "cleaning",
        "stat": "analysis", "mean": "analysis", "average": "analysis",
        "correlation": "analysis", "skew": "analysis", "distribution": "analysis",
        "chart": "visualisation", "plot": "visualisation", "graph": "visualisation",
        "histogram": "visualisation", "heatmap": "visualisation", "scatter": "visualisation",
        "boxplot": "visualisation", "visualis": "visualisation",
        "machine learning": "automl", "model": "automl", "random forest": "automl",
        "decision tree": "automl", "regression": "automl", "classification": "automl",
        "accuracy": "automl", "overfit": "automl", "cross-valid": "automl",
        "feature": "automl", "predict": "automl",
        "python": "general", "pandas": "general", "data science": "data_science_intro",
    }

    matched_topic = next(
        (v for k, v in topic_map.items() if k in query_lower),
        "general"
    )

    resources = get_resources(matched_topic, level)
    return resources


def render_resources(topic: str, level: str = "beginner") -> str:
    """
    Returns a markdown-formatted string of resource recommendations.
    """
    res = get_resources(topic, level)
    videos   = res.get("videos", [])
    articles = res.get("articles", [])

    lines = []

    if videos:
        lines.append("### 🎬 Recommended Videos")
        for v in videos:
            lines.append(f"**[{v['title']}]({v['url']})**")
            lines.append(f"📺 {v['channel']}  •  ⏱ {v['duration']}")
            lines.append(f"*{v['why']}*")
            lines.append("")

    if articles:
        lines.append("### 📰 Recommended Articles & Tutorials")
        for a in articles:
            lines.append(f"**[{a['title']}]({a['url']})**")
            lines.append(f"📖 {a['source']}")
            lines.append(f"*{a['why']}*")
            lines.append("")

    return "\n".join(lines)