"""
Agent 7 — Socratic Teaching Agent (Groq LLaMA version)
"""

import json
import os
import re
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


@dataclass
class Question:
    id: int
    text: str
    concept: str
    difficulty: str
    expected_keywords: list
    hint: str


@dataclass
class AnswerFeedback:
    score: int
    is_correct: bool
    explanation: str
    follow_up: Optional[str]
    concept_tag: str


@dataclass
class SessionResult:
    total_score: int
    max_score: int
    percentage: float
    mastered_concepts: list
    weak_concepts: list
    badge: str
    summary: str


def _build_question_prompt(analysis_summary: dict, difficulty: str, n: int) -> str:
    return f"""
You are a Socratic data science tutor. A student has just uploaded a dataset.
Here is what the automated analysis found:

{json.dumps(analysis_summary, indent=2)}

Generate exactly {n} Socratic questions at the **{difficulty}** level.

Difficulty guidelines:
- beginner     -> Observation ("What do you notice about...?")
- intermediate -> Interpretation ("Why might X cause...?")
- advanced     -> Application ("What would you do next and why?")

Cover a mix of: missing values, outliers, data types, correlation,
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


def _build_evaluation_prompt(question, user_answer, analysis_summary, prior_score):
    return f"""
You are a strict data science examiner. You do NOT give marks for effort or vague answers.
You only award marks for correct, specific, technically accurate content.

Dataset context:
{json.dumps(analysis_summary, indent=2)}

Question ({question.difficulty} level, concept: {question.concept}):
"{question.text}"

Expected keywords/ideas: {question.expected_keywords}

Student's answer:
"{user_answer}"

STRICT scoring rules — follow these exactly:
- 0   : Answer is blank, completely irrelevant, or does not address the question at all
- 1-2 : Answer mentions the topic area but shows fundamental misunderstanding
- 3-4 : Answer is on the right topic but missing all key technical reasoning
- 5-6 : Answer shows partial understanding — correct idea but lacks depth or precision
- 7-8 : Answer is mostly correct with minor gaps or missing one key point
- 9-10: Answer is complete, precise, technically accurate, and shows deep understanding

PENALTIES — automatically deduct points for:
- Generic textbook answers that do not reference this specific dataset or question: -3 points
- Answering a different question than what was asked: score must be 0-2 maximum
- Correct keywords used but in the wrong context: -2 points
- No mention of at least one expected keyword or idea: cap score at 4 maximum

Return ONLY valid JSON:
{{
  "score": <integer 0-10>,
  "is_correct": <true if score >= 7>,
  "explanation": "<2-4 sentences: be specific about what was wrong or missing>",
  "follow_up": "<one follow-up question to deepen thinking, or null>",
  "concept_tag": "{question.concept}"
}}
""".strip()


def _build_summary_prompt(feedbacks, analysis_summary, difficulty):
    results = [{"concept": f.concept_tag, "score": f.score, "correct": f.is_correct} for f in feedbacks]
    return f"""
A student completed a Socratic quiz at {difficulty} level.
Results: {json.dumps(results, indent=2)}
Dataset context: {json.dumps(analysis_summary, indent=2)}

Write a personalised 3-4 sentence summary. Mention their strongest concept
and area to study next. Be encouraging but honest.
Return ONLY plain text, no JSON, no markdown.
""".strip()


def generate_questions(analysis_summary: dict, difficulty: str = "intermediate", n: int = 5) -> list:
    prompt = _build_question_prompt(analysis_summary, difficulty, n)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a Socratic data science tutor. Return only valid JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4,
        max_tokens=1500,
    )
    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"^```[a-z]*\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)
    data = json.loads(raw)
    return [Question(**q) for q in data]


def evaluate_answer(question, user_answer: str, analysis_summary: dict, prior_score: int = 0) -> AnswerFeedback:
    if not user_answer.strip():
        return AnswerFeedback(score=0, is_correct=False, explanation="No answer provided.", follow_up=question.hint, concept_tag=question.concept)
    prompt = _build_evaluation_prompt(question, user_answer, analysis_summary, prior_score)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a strict data science examiner. Return only valid JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=600,
    )
    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"^```[a-z]*\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)
    data = json.loads(raw)
    return AnswerFeedback(**data)


def compute_session_result(feedbacks: list, analysis_summary: dict, difficulty: str) -> SessionResult:
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
    prompt = _build_summary_prompt(feedbacks, analysis_summary, difficulty)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are an encouraging data science tutor."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        max_tokens=300,
    )
    summary = response.choices[0].message.content.strip()
    return SessionResult(total_score=total, max_score=max_score, percentage=pct,
                         mastered_concepts=list(set(mastered)), weak_concepts=list(set(weak)),
                         badge=badge, summary=summary)