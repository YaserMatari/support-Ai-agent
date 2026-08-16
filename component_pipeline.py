"""
component_pipeline.py
---------------------
The ORCHESTRATOR. Wires the three agents together in order:

    message -> [classifier] -> [retriever] -> [responder] -> draft reply

Keeping this in one place means both the API and the UI import the exact same
pipeline, so they can never drift out of sync.
"""

from __future__ import annotations
from dataclasses import dataclass

from component_classifier import classify_with_self_correction, SupportClassification
from component_retriever import ToolRetriever, Policy
from component_responder import SupportResponder


@dataclass
class PipelineResult:
    """Everything the pipeline produced, so callers can inspect each stage."""
    classification: SupportClassification
    policy: Policy
    draft: str


def run_support_agent_pipeline(customer_message: str) -> PipelineResult:
    """Run all three agents and return the full, inspectable result."""
    classification = classify_with_self_correction(customer_message)
    policy = ToolRetriever().retrieve_policy(classification.category)
    draft = SupportResponder().generate_draft(customer_message, classification, policy)
    return PipelineResult(classification=classification, policy=policy, draft=draft)
