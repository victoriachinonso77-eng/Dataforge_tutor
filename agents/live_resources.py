# agents/live_resources.py
# Live Resource Agent — Searches YouTube and the web in real time
# Requires: YouTube Data API v3 key + Tavily API key

import os
import re

# ── YouTube Search ─────────────────────────────────────────────────────────
def search_youtube(query: str, max_results: int = 3,
                   api_key: str = None) -> list[dict]:
    """
    Searches YouTube for videos matching the query.
    Returns list of video dicts with title, channel, url, thumbnail, duration.
    Requires: pip install google-api-python-client
    """
    key = api_key or os.getenv("YOUTUBE_API_KEY", "")
    if not key:
        return []

    try:
        from googleapiclient.discovery import build

        youtube = build("youtube", "v3", developerKey=key)

        # Search for videos
        search_response = youtube.search().list(
            q=query,
            part="id,snippet",
            maxResults=max_results,
            type="video",
            relevanceLanguage="en",
            safeSearch="strict",          # Safe content only
            videoDuration="medium",       # 4–20 min — good for learning
        ).execute()

        videos = []
        video_ids = [item["id"]["videoId"]
                     for item in search_response.get("items", [])]

        if not video_ids:
            return []

        # Get video details (duration, view count)
        details_response = youtube.videos().list(
            part="contentDetails,statistics,snippet",
            id=",".join(video_ids)
        ).execute()

        for item in details_response.get("items", []):
            snippet  = item["snippet"]
            details  = item["contentDetails"]
            stats    = item.get("statistics", {})

            # Parse ISO 8601 duration (e.g. PT8M30S → "8 min 30 sec")
            duration_raw = details.get("duration", "PT0S")
            duration_str = _parse_duration(duration_raw)

            views = int(stats.get("viewCount", 0))
            views_str = f"{views:,} views" if views else ""

            videos.append({
                "title":     snippet.get("title", ""),
                "channel":   snippet.get("channelTitle", ""),
                "url":       f"https://www.youtube.com/watch?v={item['id']}",
                "thumbnail": snippet.get("thumbnails", {}).get("medium", {}).get("url", ""),
                "duration":  duration_str,
                "views":     views_str,
                "published": snippet.get("publishedAt", "")[:10],
                "description": snippet.get("description", "")[:200] + "...",
            })

        return videos

    except Exception as e:
        print(f"YouTube search error: {e}")
        return []


def _parse_duration(iso_duration: str) -> str:
    """Convert ISO 8601 duration to human readable string."""
    match = re.match(
        r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?',
        iso_duration
    )
    if not match:
        return ""
    hours   = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)

    if hours > 0:
        return f"{hours}h {minutes}m"
    elif minutes > 0:
        return f"{minutes} min"
    else:
        return f"{seconds} sec"


# ── Web Article Search ─────────────────────────────────────────────────────
def search_articles(query: str, max_results: int = 4,
                    api_key: str = None) -> list[dict]:
    """
    Searches the web for tutorials and articles matching the query.
    Filters to trusted educational domains.
    Requires: pip install tavily-python
    """
    key = api_key or os.getenv("TAVILY_API_KEY", "")
    if not key:
        return []

    try:
        from tavily import TavilyClient

        client = TavilyClient(api_key=key)

        # Add "tutorial" to bias towards educational content
        search_query = f"{query} tutorial guide"

        response = client.search(
            query=search_query,
            search_depth="basic",
            max_results=max_results + 3,  # Get extra to filter
            include_domains=[
                # Trusted educational and data science sources
                "towardsdatascience.com",
                "realpython.com",
                "kaggle.com",
                "scikit-learn.org",
                "pandas.pydata.org",
                "numpy.org",
                "plotly.com",
                "streamlit.io",
                "medium.com",
                "analyticsvidhya.com",
                "datacamp.com",
                "w3schools.com",
                "geeksforgeeks.org",
                "machinelearningmastery.com",
                "developer.mozilla.org",
                "docs.python.org",
                "stackoverflow.com",
                "github.com",
                "ibm.com",
                "google.com",
                "developers.google.com",
                "coursera.org",
                "edx.org",
            ]
        )

        articles = []
        seen_domains = set()

        for result in response.get("results", []):
            url     = result.get("url", "")
            title   = result.get("title", "")
            content = result.get("content", "")
            score   = result.get("score", 0)

            # Extract domain for display
            domain_match = re.search(r'https?://(?:www\.)?([^/]+)', url)
            domain = domain_match.group(1) if domain_match else url

            # Skip duplicates from same domain
            if domain in seen_domains:
                continue
            seen_domains.add(domain)

            # Skip if no meaningful content
            if not title or len(content) < 50:
                continue

            articles.append({
                "title":   title,
                "url":     url,
                "source":  domain,
                "snippet": content[:250] + "..." if len(content) > 250 else content,
                "score":   score,
            })

            if len(articles) >= max_results:
                break

        return articles

    except Exception as e:
        print(f"Web search error: {e}")
        return []


# ── Combined Resource Fetcher ──────────────────────────────────────────────
def fetch_live_resources(topic: str, level: str = "beginner",
                         youtube_key: str = None,
                         tavily_key: str = None) -> dict:
    """
    Fetches live YouTube videos and web articles for a given topic.
    Automatically builds appropriate search queries per topic and level.
    """

    # Build search queries based on topic and level
    level_suffix = "for beginners" if level == "beginner" else "intermediate advanced"

    query_map = {
        "data_science_intro": f"what is data science {level_suffix}",
        "cleaning":           f"data cleaning pandas python {level_suffix}",
        "analysis":           f"exploratory data analysis EDA statistics {level_suffix}",
        "visualisation":      f"data visualisation python matplotlib plotly {level_suffix}",
        "automl":             f"machine learning {level_suffix} scikit-learn",
        "missing_values":     f"handling missing values pandas {level_suffix}",
        "outliers":           f"outlier detection python {level_suffix}",
        "correlation":        f"correlation analysis python {level_suffix}",
        "regression":         f"linear regression machine learning {level_suffix}",
        "classification":     f"classification machine learning {level_suffix}",
        "random_forest":      f"random forest algorithm explained {level_suffix}",
        "decision_tree":      f"decision tree machine learning {level_suffix}",
        "overfitting":        f"overfitting underfitting machine learning {level_suffix}",
        "cross_validation":   f"cross validation machine learning {level_suffix}",
        "feature_importance": f"feature importance machine learning {level_suffix}",
        "histogram":          f"histogram data visualisation {level_suffix}",
        "box_plot":           f"box plot interquartile range {level_suffix}",
        "heatmap":            f"correlation heatmap seaborn {level_suffix}",
    }

    query = query_map.get(topic, f"data science {topic} {level_suffix}")

    # Fetch in parallel-ish
    videos   = search_youtube(query, max_results=3, api_key=youtube_key)
    articles = search_articles(query, max_results=4, api_key=tavily_key)

    return {
        "topic":    topic,
        "level":    level,
        "query":    query,
        "videos":   videos,
        "articles": articles,
        "live":     True,
    }


def get_topic_from_question(question: str) -> str:
    """
    Detects which data science topic a question is about.
    Used by the chat tab to fetch relevant resources.
    """
    q = question.lower()
    topic_keywords = {
        "cleaning":         ["clean","missing","null","duplicate","outlier","impute","preprocess"],
        "analysis":         ["mean","average","median","std","standard deviation","correlation",
                            "statistic","skew","distribution","eda","exploratory"],
        "visualisation":    ["chart","plot","graph","histogram","heatmap","scatter","boxplot",
                            "visualis","matplotlib","plotly","seaborn"],
        "automl":           ["machine learning","model","accuracy","overfit","underfit",
                            "random forest","decision tree","regression","classification",
                            "cross valid","feature","predict","train","test"],
        "data_science_intro":["data science","what is","pipeline","workflow"],
    }
    for topic, keywords in topic_keywords.items():
        if any(kw in q for kw in keywords):
            return topic
    return "data_science_intro"