# 🤖 Customer Support AI Agent — Modular Multi-Agent Pipeline

A small, production-minded **multi-agent** system that turns a raw customer
message into a policy-grounded draft reply. It's built to demonstrate the
patterns that keep LLM systems reliable: **modular separation of concerns**,
**Pydantic schema guardrails**, a **self-correcting retry boundary**, a
**FastAPI** service, a **Streamlit** dashboard, and **Docker** packaging.

The whole thing runs **offline with no API key** thanks to a simulated LLM,
so anyone can clone it and see it work in seconds. Swapping in a real model is
a one-file change.

---

## The pipeline

```
customer message
      │
      ▼
┌───────────────┐   validated       ┌───────────────┐   Policy        ┌───────────────┐
│  Agent 1      │  classification   │  Agent 2      │  object         │  Agent 3      │
│  CLASSIFIER   │ ────────────────▶ │  RETRIEVER    │ ──────────────▶ │  RESPONDER    │ ──▶ draft reply
│ (self-correct)│                   │ (policy KB)   │                 │ (policy-      │
└───────────────┘                   └───────────────┘                 │  grounded)    │
                                                                       └───────────────┘
```

Each agent does exactly one job, which avoids the "God Agent" problem where a
single giant prompt tries to do everything and becomes impossible to debug.

| File | Role |
|------|------|
| `component_llm.py` | The single LLM boundary. Swap this to go from simulated to real. |
| `component_classifier.py` | **Agent 1.** Free text → validated `{category, urgency, summary}`, with self-correcting retries. |
| `component_retriever.py` | **Agent 2.** Category → structured company `Policy`. |
| `component_responder.py` | **Agent 3.** Classification + policy → drafted reply. |
| `component_pipeline.py` | Orchestrator that runs all three in order. |
| `app.py` | FastAPI service (`/`, `/classify`, `/resolve`). |
| `app_web.py` | Streamlit dashboard that runs the pipeline step by step. |
| `tests/test_pipeline.py` | Tests that prove the guardrails behave. |

---

## Key design ideas

**Schema guardrails.** The classifier's output is validated against a strict
Pydantic model with `Literal` types. The model can't return a category or
urgency outside the allowed set without the system noticing.

**Self-correcting retry boundary.** If validation fails, the exact error is fed
back to the model and it retries. After `max_retries`, a guaranteed-valid
fallback is returned, so the pipeline never crashes or returns `None`.

**Retrieval that actually grounds the answer.** The retriever returns a
structured `Policy`, and the responder builds its reply *from those fields*.
Edit a policy (say, change the goodwill credit) and the customer-facing reply
changes with it — the knowledge base genuinely drives the output.

**One LLM boundary.** Every model call lives in `component_llm.py`. Going live
means editing that one file; nothing else changes.

---

## Run it locally

Requires Python 3.10+ (developed and tested on 3.12).

```bash
# 1. clone, then create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. install
pip install -r requirements.txt

# 3a. run the Streamlit dashboard
streamlit run app_web.py         # opens http://localhost:8501

# 3b. or run the API
uvicorn app:app --reload         # docs at http://127.0.0.1:8000/docs
```

Try the API from the command line:

```bash
curl -X POST http://127.0.0.1:8000/resolve \
     -H "Content-Type: application/json" \
     -d '{"message": "I was charged twice on my invoice, refund me!"}'
```

## Run the tests

```bash
pip install -r requirements-dev.txt
pytest -q
```

## Run in Docker

```bash
docker compose up --build
# API -> http://localhost:8000/docs
# UI  -> http://localhost:8501
```

---

## Making it real

Open `component_llm.py` and replace the body of `generate_response` with a real
API call (there's a ready-to-adapt Anthropic snippet in the comments). Because
every other module depends only on this boundary, no other file changes.

---

## What was hardened in this version

- Dockerfile now **serves** the app (`uvicorn`, exposed port, `0.0.0.0`) instead
  of running a Streamlit script with `python`, which would exit immediately.
- Validation error formatting rewritten so it imports on **Python 3.10/3.11**,
  not just 3.12.
- The retriever's policy is now **actually used** by the responder.
- The responder no longer promises a refund on **every** billing message; the
  reply and any escalation are driven by policy + urgency data.
- Classifier always returns a valid object (safe fallback) instead of possibly
  returning `None`.
- API exposes the **full pipeline**, not just classification.
- Added a test suite, `docker-compose.yml`, `.dockerignore`, and `.gitignore`.
