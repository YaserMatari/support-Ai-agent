"""
component_retriever.py
----------------------
Agent 2 of 3: the RETRIEVER (a stand-in for a RAG / knowledge-base lookup).

Given a category, it returns the relevant company policy as a *structured*
object. Because the responder builds its reply from these fields, editing a
policy here genuinely changes what the customer is told -- the retrieval step
actually grounds the final answer instead of being decorative.
"""

from __future__ import annotations
from pydantic import BaseModel, Field


class Policy(BaseModel):
    """A single, structured company policy entry."""
    category: str
    headline: str = Field(description="Short human-readable policy name.")
    entitlement: str = Field(description="What the customer may be entitled to.")
    action: str = Field(description="The next step support will take.")
    requires_human: bool = Field(
        default=False, description="Whether a human must be looped in."
    )
    raw_text: str = Field(description="The full policy text, for display/audit.")


class ToolRetriever:
    """Looks up the policy that applies to a given category."""

    def __init__(self) -> None:
        self._policy_db: dict[str, Policy] = {
            "billing": Policy(
                category="billing",
                headline="Billing & Refunds Policy",
                entitlement=(
                    "a full refund for any verified duplicate charge, usually "
                    "processed within 5-7 business days"
                ),
                action=(
                    "I've flagged your account for a billing review so the team "
                    "can confirm the charges."
                ),
                requires_human=False,
                raw_text=(
                    "BILLING POLICY:\n"
                    "- Refund requests are honoured within 30 days of purchase.\n"
                    "- Verified duplicate/double charges are refunded in full.\n"
                    "- Refunds settle in 5-7 business days."
                ),
            ),
            "technical": Policy(
                category="technical",
                headline="Technical Support Policy",
                entitlement=(
                    "step-by-step troubleshooting and, if needed, escalation to "
                    "engineering"
                ),
                action=(
                    "Please try these steps first: 1) clear your cache, "
                    "2) retry in an incognito window, 3) restart the app."
                ),
                requires_human=False,
                raw_text=(
                    "TECH POLICY:\n"
                    "- First-line steps: clear cache, incognito, restart.\n"
                    "- If unresolved, collect logs and escalate to engineering."
                ),
            ),
            "complaint": Policy(
                category="complaint",
                headline="Complaint Handling Policy",
                entitlement="a sincere apology and a $15 goodwill service credit",
                action="I've noted your feedback on your account.",
                requires_human=True,
                raw_text=(
                    "COMPLAINT POLICY:\n"
                    "- Acknowledge the customer's experience with empathy.\n"
                    "- Offer a $15 service credit as a goodwill gesture.\n"
                    "- Escalate high-urgency complaints to a manager."
                ),
            ),
        }

    def retrieve_policy(self, category: str) -> Policy:
        """Return the Policy for a category, or a safe generic fallback."""
        return self._policy_db.get(
            category.lower(),
            Policy(
                category="general",
                headline="General Support Policy",
                entitlement="assistance from a support specialist",
                action="I'm routing your message to a human agent.",
                requires_human=True,
                raw_text="GENERAL POLICY: Route to a human agent.",
            ),
        )
