"""
Agent 7 — Socratic Teaching Agent
Generates dataset-aware questions, evaluates user answers,
adapts difficulty, and produces a Data Science Readiness Score.
"""

import json
import os
import re
from dataclasses import dataclass, field
from typing import Optional
from anthropic import Anthropic

client = Anthropic()

# ─── Data classes ────────────────────────────────────────────────────────────

@dataclass
class Question:
    id: int
    text: str
    concept: str          # e.g. "missing values", "correlation", "skewness"
    difficulty: str       # "beginner" | "intermediate" | "advanced"
    expected_keywords: list[str]
    hint: str


@dataclass
class AnswerFeedback:
    score: int            # 0–10
    is_correct: bool
    explanation: str
    follow_up: Optional[str]
    concept_tag: str


@dataclass
class SessionResult:
    total_score: int
    max_score: int
    percentage: float
    mastered_concepts: list[str]
    weak_concepts: list[str]
    badge: str            # "Novice" | "Analyst" | "Data Scientist" | "Expert"
    summary: str


# ─── Prompt builders ─────────────────────────────────────────────────────────

def _build_question_prompt(analysis_summary: dict, difficulty: str, n: int) -> str:
    return f"""
You are a Socratic data science tutor. A student has just uploaded a dataset.
Here is what the automated analysis found:

{json.dumps(analysis_summary, indent=2)}

Your job: generate exactly {n} Socratic questions at the **{difficulty}** level.

Difficulty guidelines:
- beginner    → Observation ("What do you notice about…?")
- intermediate → Interpretation ("Why might X cause…?", "What does Y imply?")
- advanced     → Application ("What would you do next and why?", "How would you handle…?")

Cover a mix of these concepts where relevant to the data:
missing values, outliers, data types, correlation, distribution shape,
skewness, feature engineering, normalisation, model selection, bias.

Return ONLY a valid JSON array. No markdown, no explanation. Schema:
[
  {{
    "id": 1,
    "text": "<the question>",
    "concept": "<one concept tag>",
    "difficulty": "{difficulty}",
    "expected_keywords": ["keyword1", "keyword2"],
    "hint": "<a gentle hint if the student is stuck>"
  }}
]
""".strip()


def _build_evaluation_prompt(
    question: Question,
    user_answer: str,
    analysis_summary: dict,
    prior_score: int,
) -> str:
    return f"""
You are a strict but encouraging data science tutor.

Dataset context:
{json.dumps(analysis_summary, indent=2)}

Question asked ({question.difficulty} level, concept: {question.concept}):
"{question.text}"

Expected keywords/ideas: {question.expected_keywords}

Student's answer:
"{user_answer}"

Their running score so far: {prior_score} points.

Evaluate the answer and return ONLY valid JSON. Schema:
{{
  "score": <integer 0–10>,
  "is_correct": <true if score >= 6>,
  "explanation": "<2–4 sentences: what was right, what was missing, the correct reasoning>",
  "follow_up": "<optional 1 follow-up question to deepen thinking, or null>",
  "concept_tag": "{question.concept}"
}}

Scoring guide:
- 9–10: Complete, precise, shows deep understanding
- 7–8 : Mostly correct with minor gaps
- 5–6 : Partially correct, key idea present
- 3–4 : Some relevant ideas but mostly off
- 0–2 : Incorrect or irrelevant
""".strip()


def _build_summary_prompt(
    feedbacks: list[AnswerFeedback],
    analysis_summary: dict,
    difficulty: str,
) -> str:
    results = [
        {"concept": f.concept_tag, "score": f.score, "correct": f.is_correct}
        for f in feedbacks
    ]
    return f"""
A student completed a Socratic quiz on a dataset at {difficulty} level.
Here are their results per question:
{json.dumps(results, indent=2)}

Dataset analysis context:
{json.dumps(analysis_summary, indent=2)}

Write a personalised 3–4 sentence summary of their performance.
Mention their strongest concept and the area they should study next.
Be encouraging but honest.
Return ONLY the plain text summary, no JSON, no markdown.
""".strip()


# ─── Core agent functions ─────────────────────────────────────────────────────

def generate_questions(
    analysis_summary: dict,
    difficulty: str = "intermediate",
    n: int = 5,
) -> list[Question]:
    """Call Claude to generate Socratic questions from the dataset analysis."""
    prompt = _build_question_prompt(analysis_summary, difficulty, n)

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()

    # Strip accidental markdown fences
    raw = re.sub(r"^```[a-z]*\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)

    data = json.loads(raw)
    return [Question(**q) for q in data]


def evaluate_answer(
    question: Question,
    user_answer: str,
    analysis_summary: dict,
    prior_score: int = 0,
) -> AnswerFeedback:
    """Call Claude to grade a student's answer and return structured feedback."""
    if not user_answer.strip():
        return AnswerFeedback(
            score=0,
            is_correct=False,
            explanation="No answer provided.",
            follow_up=question.hint,
            concept_tag=question.concept,
        )

    prompt = _build_evaluation_prompt(question, user_answer, analysis_summary, prior_score)

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()
    raw = re.sub(r"^```[a-z]*\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)

    data = json.loads(raw)
    return AnswerFeedback(**data)


def compute_session_result(
    feedbacks: list[AnswerFeedback],
    analysis_summary: dict,
    difficulty: str,
) -> SessionResult:
    """Aggregate all feedback into a final session result with badge and summary."""
    total = sum(f.score for f in feedbacks)
    max_score = len(feedbacks) * 10
    pct = round((total / max_score) * 100) if max_score > 0 else 0

    mastered = [f.concept_tag for f in feedbacks if f.score >= 7]
    weak = [f.concept_tag for f in feedbacks if f.score < 5]

    if pct >= 85:
        badge = "🏆 Expert"
    elif pct >= 70:
        badge = "🎓 Data Scientist"
    elif pct >= 50:
        badge = "📊 Analyst"
    else:
        badge = "🌱 Novice"

    # Generate personalised summary via Claude
    prompt = _build_summary_prompt(feedbacks, analysis_summary, difficulty)
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    summary = response.content[0].text.strip()

    return SessionResult(
        total_score=total,
        max_score=max_score,
        percentage=pct,
        mastered_concepts=list(set(mastered)),
        weak_concepts=list(set(weak)),
        badge=badge,
        summary=summary,
    )
