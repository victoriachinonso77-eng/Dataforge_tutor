# agents/socratic.py
# Agent 7 — Socratic Teaching Agent (OpenAI GPT-4)

import json
import os
import re
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

groq_client = None
if os.getenv("GROQ_API_KEY"):
    try:
        from groq import Groq
        groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    except Exception as e:
        print(f"Groq init error: {e}")


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


BADGES = {
    "Expert":         {"min_pct": 85, "emoji": "🏆", "color": "#F59E0B"},
    "Data Scientist": {"min_pct": 70, "emoji": "🔬", "color": "#8B5CF6"},
    "Analyst":        {"min_pct": 50, "emoji": "📊", "color": "#3B82F6"},
    "Novice":         {"min_pct": 0,  "emoji": "🌱", "color": "#6B7280"},
}

DIFFICULTY_LABELS = {
    "beginner":     "Beginner",
    "intermediate": "Intermediate",
    "advanced":     "Advanced",
}


def get_badge(total_score: int, max_score: int) -> dict:
    pct = (total_score / max(max_score, 1)) * 100
    earned = {**BADGES["Novice"], "name": "Novice", "pct": round(pct, 1)}
    for name, info in BADGES.items():
        if pct >= info["min_pct"]:
            earned = {**info, "name": name, "pct": round(pct, 1)}
    return earned


def _call_llm(system_prompt, user_prompt, max_tokens=1500,
              temperature=0.4, gpt_client=None):
    if groq_client:
        try:
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Groq error, falling back to GPT-4: {e}")
    if gpt_client:
        try:
            response = gpt_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"GPT-4 error: {e}")
    raise RuntimeError("No LLM available")


def _clean_json(raw):
    raw = re.sub(r"^```[a-z]*\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)
    return raw.strip()


def generate_questions(analysis_summary, difficulty="intermediate",
                        n=5, gpt_client=None):
    prompt = f"""You are a Socratic data science tutor.
Dataset analysis: {json.dumps(analysis_summary, indent=2)}
Generate exactly {n} Socratic questions at {difficulty} level.
Return ONLY a valid JSON array with schema:
[{{"id":1,"text":"question","concept":"concept","difficulty":"{difficulty}","expected_keywords":["kw1"],"hint":"hint"}}]"""
    try:
        raw = _call_llm("Return only valid JSON.", prompt,
                         max_tokens=1500, temperature=0.4, gpt_client=gpt_client)
        data = json.loads(_clean_json(raw))
        return [Question(**q) for q in data]
    except Exception as e:
        print(f"Question generation error: {e}")
        return _fallback_questions(difficulty)


def evaluate_answer(question, user_answer, analysis_summary,
                     prior_score=0, gpt_client=None):
    if not user_answer.strip():
        return AnswerFeedback(score=0, is_correct=False,
                               explanation="No answer provided.",
                               follow_up=question.hint,
                               concept_tag=question.concept)
    prompt = f"""Grade this answer strictly 0-10.
Question: {question.text}
Expected keywords: {question.expected_keywords}
Student answer: "{user_answer}"
Penalise generic answers not referencing the dataset.
Return ONLY JSON: {{"score":0,"is_correct":false,"explanation":"...","follow_up":"...","concept_tag":"{question.concept}"}}"""
    try:
        raw = _call_llm("You are a strict examiner. Return only valid JSON.",
                         prompt, max_tokens=600, temperature=0.3,
                         gpt_client=gpt_client)
        data = json.loads(_clean_json(raw))
        return AnswerFeedback(**data)
    except Exception as e:
        print(f"Evaluation error: {e}")
        return _fallback_grade(user_answer, question.concept)


def compute_session_result(feedbacks, analysis_summary,
                            difficulty, gpt_client=None):
    total = sum(f.score for f in feedbacks)
    max_score = len(feedbacks) * 10
    pct = round((total / max_score) * 100) if max_score > 0 else 0
    mastered = [f.concept_tag for f in feedbacks if f.score >= 7]
    weak = [f.concept_tag for f in feedbacks if f.score < 5]
    badge_info = get_badge(total, max_score)
    badge = f"{badge_info['emoji']} {badge_info['name']}"
    try:
        prompt = f"""Write a 3-sentence encouraging summary for a student who scored {pct}%.
Strong: {mastered}. Weak: {weak}. Return plain text only."""
        summary = _call_llm("You are an encouraging tutor.", prompt,
                              max_tokens=300, temperature=0.5,
                              gpt_client=gpt_client)
    except Exception:
        summary = (f"You scored {pct}% — {badge}. "
                   f"Strong areas: {', '.join(set(mastered)) or 'keep practising'}. "
                   f"Focus next on: {', '.join(set(weak)) or 'all areas'}.")
    return SessionResult(total_score=total, max_score=max_score,
                          percentage=pct, mastered_concepts=list(set(mastered)),
                          weak_concepts=list(set(weak)), badge=badge, summary=summary)


def _fallback_questions(difficulty):
    questions = {
        "beginner": [
            Question(id=1, text="What is a missing value and why does it matter?",
                     concept="Missing values", difficulty="beginner",
                     expected_keywords=["empty","null","distort","median"],
                     hint="Think about what happens to averages when data is incomplete."),
            Question(id=2, text="What does it mean when two columns are correlated?",
                     concept="Correlation", difficulty="beginner",
                     expected_keywords=["relationship","together","r value"],
                     hint="Think about how one variable moves when the other changes."),
            Question(id=3, text="Why do we remove duplicate rows before analysis?",
                     concept="Data cleaning", difficulty="beginner",
                     expected_keywords=["skew","inflate","integrity"],
                     hint="What happens to counts if a row appears twice?"),
        ],
        "intermediate": [
            Question(id=1, text="Why was median imputation chosen over mean?",
                     concept="Imputation", difficulty="intermediate",
                     expected_keywords=["outlier","robust","skewed"],
                     hint="Think about what outliers do to the mean vs median."),
            Question(id=2, text="What does high skewness imply for ML models?",
                     concept="Skewness", difficulty="intermediate",
                     expected_keywords=["assumption","log transform","normality"],
                     hint="Many models assume normally distributed features."),
        ],
        "advanced": [
            Question(id=1, text="What are the ethical implications of the bias warnings flagged?",
                     concept="AI ethics", difficulty="advanced",
                     expected_keywords=["discrimination","protected","EU AI Act"],
                     hint="Consider who might be negatively affected."),
            Question(id=2, text="How would you validate that the best model generalises?",
                     concept="Model validation", difficulty="advanced",
                     expected_keywords=["cross-validation","hold-out","overfitting"],
                     hint="What techniques prevent overly optimistic performance?"),
        ],
    }
    return questions.get(difficulty, questions["beginner"])


def _fallback_grade(answer, concept):
    if not answer or len(answer.strip()) < 10:
        return AnswerFeedback(score=0, is_correct=False,
                               explanation="Answer too short.",
                               follow_up="Please provide more detail.",
                               concept_tag=concept)
    score = min(5, max(1, len(answer.split()) // 10))
    return AnswerFeedback(score=score, is_correct=score >= 7,
                           explanation="Auto-graded — add API key for detailed feedback.",
                           follow_up="Can you add more specific detail?",
                           concept_tag=concept)
