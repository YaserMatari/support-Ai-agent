"""
component_classifier.py
-----------------------
Agent 1 of 3: the CLASSIFIER.

Its job: turn a free-text customer message into a small, *validated* structured
object (category / urgency / summary) the rest of the pipeline can rely on.

The key idea is the "self-correcting retry boundary": the model's raw output is
never trusted directly. It is parsed and validated against a strict Pydantic
schema; if it fails, the exact validation error is fed back to the model so it
can try again. After a set number of attempts we fall back to a safe default
instead of crashing.
"""

from __future__ import annotations
import json
import time
from typing import Literal

from pydantic import BaseModel, Field, ValidationError

from component_llm import SimulatedLLM


class SupportClassification(BaseModel):
    """The strict contract every classification must satisfy."""
    category: Literal["billing", "technical", "complaint"] = Field(
        description="Which team should own this issue."
    )
    urgency: Literal["low", "medium", "high"] = Field(
        description="How urgent the customer's tone/situation is."
    )
    summary: str = Field(description="One-sentence summary of the problem.")


def classify_with_self_correction(
    customer_message: str,
    max_retries: int = 3,
    retry_delay: float = 0.0,
) -> SupportClassification:
    """Classify a message, retrying with feedback until it validates.

    Parameters
    ----------
    customer_message : the raw text from the customer.
    max_retries      : how many times to ask the model before giving up.
    retry_delay      : optional pause between attempts (seconds). Kept at 0 so
                       the API stays responsive; raise it if you wire in a real
                       rate-limited model.
    """
    llm = SimulatedLLM()
    system_instruction = (
        "You are an AI routing agent. Respond strictly in JSON matching the "
        "SupportClassification schema (category, urgency, summary)."
    )
    current_prompt = f"System: {system_instruction}\nUser: {customer_message}"
    last_error = "no attempts were made"

    for attempt in range(1, max_retries + 1):
        raw_output = llm.generate_response(current_prompt)
        try:
            parsed = json.loads(raw_output)
            return SupportClassification(**parsed)
        except (ValidationError, json.JSONDecodeError) as err:
            last_error = str(err)
            feedback = (
                parse_errors(err)
                if isinstance(err, ValidationError)
                else f"Your output was not valid JSON: {err}"
            )
            # Append the failed answer + the correction so a real model can see
            # what went wrong and fix it on the next attempt.
            current_prompt += (
                f"\n\nAssistant: {raw_output}\nSystem Correction: {feedback}"
            )
            if retry_delay:
                time.sleep(retry_delay)

    # Every attempt failed -> never crash the pipeline; return a safe default.
    return execute_safety_fallback(customer_message, last_error)


def parse_errors(error: ValidationError) -> str:
    """Turn a Pydantic ValidationError into plain-language correction notes."""
    lines = []
    for e in error.errors():
        location = " -> ".join(str(part) for part in e["loc"])
        got = e.get("input")
        lines.append(f"- Field '{location}': {e['msg']} (got: {got!r})")
    return (
        "Your previous JSON failed validation:\n"
        + "\n".join(lines)
        + "\nReturn corrected JSON that matches the schema."
    )


def execute_safety_fallback(message: str, error: str) -> SupportClassification:
    """A guaranteed-valid classification used when the model can't produce one."""
    return SupportClassification(
        category="technical",
        urgency="medium",
        summary=f"[SYSTEM FALLBACK] Could not classify automatically ({error[:60]}...).",
    )
