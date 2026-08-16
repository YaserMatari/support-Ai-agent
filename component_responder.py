"""
component_responder.py
----------------------
Agent 3 of 3: the RESPONDER.

Given the validated classification AND the retrieved policy, it drafts the
customer-facing reply. The wording is built from the *policy* fields, so what
the customer is promised always matches the current policy in the retriever --
and it no longer blindly promises a refund for every billing message.
"""

from __future__ import annotations

from component_classifier import SupportClassification
from component_retriever import Policy


class SupportResponder:
    """Composes a polite, policy-grounded draft reply."""

    def generate_draft(
        self,
        message: str,
        classification: SupportClassification,
        policy: Policy,
    ) -> str:
        salutation = "Hello,"
        closing = "Best regards,\nCustomer Support Team"

        # A manager is looped in when the policy demands it OR the situation is
        # high urgency -- decided by data, not hard-coded per category.
        escalate = policy.requires_human or classification.urgency == "high"
        escalation_line = (
            " I've also escalated this to a manager for a faster resolution."
            if escalate else ""
        )

        # The body is assembled from the POLICY fields, so changing a policy in
        # the retriever changes the reply produced here.
        body = (
            f'Thank you for contacting us. I understand the issue as: '
            f'"{classification.summary}"\n\n'
            f"Under our {policy.headline}, you may be entitled to "
            f"{policy.entitlement}. {policy.action}{escalation_line}"
        )

        return f"{salutation}\n\n{body}\n\n{closing}"
