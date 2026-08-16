"""
app.py
------
FastAPI service. Exposes the pipeline over HTTP so other systems can call it.

Run locally:
    uvicorn app:app --reload
Then open http://127.0.0.1:8000/docs for interactive, auto-generated API docs.
"""

from __future__ import annotations
from fastapi import FastAPI
from pydantic import BaseModel

from component_classifier import classify_with_self_correction
from component_pipeline import run_support_agent_pipeline

app = FastAPI(title="AI Support Agent API", version="1.0.0")


class CustomerEmail(BaseModel):
    """Request body: the raw customer message."""
    message: str


@app.get("/")
def health() -> dict:
    """Simple health check so you can confirm the service is up."""
    return {"status": "ok", "service": "AI Support Agent API"}


@app.post("/classify")
def classify(email: CustomerEmail) -> dict:
    """Run only the classifier agent (fast triage)."""
    result = classify_with_self_correction(email.message)
    return {
        "status": "success",
        "category": result.category,
        "urgency": result.urgency,
        "summary": result.summary,
    }


@app.post("/resolve")
def resolve(email: CustomerEmail) -> dict:
    """Run the full three-agent pipeline and return the drafted reply."""
    result = run_support_agent_pipeline(email.message)
    return {
        "status": "success",
        "classification": result.classification.model_dump(),
        "policy": result.policy.model_dump(),
        "draft": result.draft,
    }
