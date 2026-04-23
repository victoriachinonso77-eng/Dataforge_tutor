
# DataForge — AI Data Science Tutor
## Agentic AI | Multi-Agent System | AI in Education

DataForge is a multi-agent AI system that autonomously cleans, analyses, visualises,
and reports on any dataset — while teaching the user data science at every step.

---

## Project Structure

```
DataForge/
│
├── app.py                          # Streamlit UI — main entry point (6 tabs)
├── orchestrator.py                 # LangChain pipeline coordinator
├── requirements.txt                # All Python dependencies
├── .env                            # API keys (never commit this)
├── README.md                       # This file
│
└── agents/
    ├── __init__.py                 # Package initialiser
    ├── cleaner.py                  # Agent 1 — Data cleaning & validation
    ├── analyser.py                 # Agent 2 — Statistical analysis
    ├── visualiser.py               # Agent 3 — Static Matplotlib charts
    ├── visualiser_plotly.py        # Agent 3v2 — Interactive Plotly charts
    ├── reporter.py                 # Agent 4 — Report writing
    ├── automl.py                   # Agent 5 — AutoML model selection
    ├── nl_query.py                 # Agent 6 — Natural language querying
    ├── tutor.py                    # Tutor — Lessons, quizzes, scoring
    ├── gpt_tutor.py               # GPT-4 — Personalised teaching
    ├── resources.py                # Resources — Curated fallback list
    └── live_resources.py           # Resources — Live YouTube + web search
```

---

## Setup Instructions

### Step 1 — Clone or create the project folder
```bash
mkdir DataForge
cd DataForge
```

### Step 2 — Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Set up API keys (all optional)
Create a `.env` file in the root folder:
```
OPENAI_API_KEY=sk-your-key-here
YOUTUBE_API_KEY=AIza-your-key-here
TAVILY_API_KEY=tvly-your-key-here
GROQ_API_KEY=
```

### Step 5 — Run the app
```bash
streamlit run app.py
```

App opens at: http://localhost:8501

---

## API Keys — Where to Get Them

| Key | Where | Cost |
|-----|-------|------|
| OpenAI | platform.openai.com | Pay per use |
| YouTube Data API v3 | console.cloud.google.com | Free (10,000 req/day) |
| Tavily | tavily.com | Free (1,000 req/month) |

All keys are optional — the app works fully offline without them.

---

## Agents Overview

| Agent | File | Job |
|-------|------|-----|
| Orchestrator | orchestrator.py | Coordinates all agents in sequence |
| Cleaner | agents/cleaner.py | Removes duplicates, fills nulls, flags outliers |
| Analyser | agents/analyser.py | Statistics, correlations, skewness, bias |
| Visualiser | agents/visualiser_plotly.py | Interactive Plotly charts |
| Reporter | agents/reporter.py | Writes 7-section analysis report |
| AutoML | agents/automl.py | Tests 5 ML models, picks best |
| NL Query | agents/nl_query.py | Answers plain English data questions |
| GPT Tutor | agents/gpt_tutor.py | Personalised GPT-4 lessons and quizzes |
| Resources | agents/live_resources.py | YouTube + web search for learning materials |

---

## Tech Stack

- Python 3.12
- Streamlit — web interface
- LangChain — agent orchestration
- Pandas / NumPy — data processing
- Plotly / Matplotlib / Seaborn — visualisation
- scikit-learn — AutoML
- OpenAI GPT-4 — teaching and reports
- YouTube Data API — live video search
- Tavily — live article search
- python-dotenv — environment management
- GitHub — version control
