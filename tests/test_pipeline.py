"""
Basic tests that prove each fix works. Run from the project root with:

    pytest -q
"""
from component_classifier import (
    classify_with_self_correction,
    SupportClassification,
)
from component_retriever import ToolRetriever
from component_responder import SupportResponder
from component_pipeline import run_support_agent_pipeline


def test_self_correction_recovers_from_bad_first_answer():
    # Billing message: the LLM is wrong on attempt 1, corrected on attempt 2.
    result = classify_with_self_correction("I was charged twice on my invoice")
    assert isinstance(result, SupportClassification)
    assert result.category == "billing"


def test_fallback_when_out_of_retries():
    # Only one attempt allowed -> the invalid first answer can't be fixed,
    # so the pipeline must fall back safely rather than return None or crash.
    result = classify_with_self_correction("invoice double charge", max_retries=1)
    assert result.summary.startswith("[SYSTEM FALLBACK]")


def test_response_is_grounded_in_policy():
    # Changing the policy must change the reply -> retrieval really matters now.
    cls = SupportClassification(category="billing", urgency="high", summary="x")
    real = ToolRetriever().retrieve_policy("billing")
    swapped = real.model_copy(update={"entitlement": "A_UNIQUE_MARKER_STRING"})
    draft = SupportResponder().generate_draft("msg", cls, swapped)
    assert "A_UNIQUE_MARKER_STRING" in draft


def test_full_pipeline_runs():
    out = run_support_agent_pipeline("The app keeps crashing on login")
    assert out.draft
    assert out.classification.category in {"billing", "technical", "complaint"}
