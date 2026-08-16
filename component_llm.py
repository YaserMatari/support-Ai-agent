"""
component_llm.py
----------------
The Large Language Model (LLM) boundary for the whole pipeline.

Every call that would normally hit a paid API (Anthropic, OpenAI, ...) lives
behind this ONE class. That gives the project two big wins:

  1. The rest of the code never touches a real network service, so the whole
     demo runs offline with no API key and no cost.
  2. When you want real intelligence, you change ONLY this file: swap the body
     of `generate_response` for a real API call, and the classifier, retriever,
     responder, API and UI all keep working unchanged.
"""

from __future__ import annotations
import json


class SimulatedLLM:
    """A deterministic stand-in for a real chat model.

    It fakes just enough behaviour to exercise every path in the pipeline,
    including a deliberate first-attempt mistake so the classifier's
    self-correction loop has something real to correct.
    """

    def __init__(self) -> None:
        # Counts how many times THIS instance has been asked to respond.
        # A fresh instance is created per classification request, so the count
        # restarts each time -- exactly what the retry demo needs.
        self.attempts = 0

    def generate_response(self, prompt: str) -> str:
        """Return a JSON string that mimics a model's structured output."""
        self.attempts += 1
        text = prompt.lower()

        # --- Billing intent -------------------------------------------------
        if any(w in text for w in ("invoice", "billing", "charged", "refund")):
            if self.attempts == 1:
                # Deliberately WRONG on the first try: "refund" is not a valid
                # category and "extremely high" is not a valid urgency. This
                # forces the classifier to catch the error and retry.
                return json.dumps({
                    "category": "refund",
                    "urgency": "extremely high",
                    "summary": "Charged twice.",
                })
            # Corrected, schema-valid answer on the retry.
            return json.dumps({
                "category": "billing",
                "urgency": "high",
                "summary": "Customer was double-charged and is requesting a refund.",
            })

        # --- Complaint intent ----------------------------------------------
        if any(w in text for w in ("terrible", "awful", "worst", "angry",
                                   "unacceptable", "disappointed", "rude")):
            return json.dumps({
                "category": "complaint",
                "urgency": "high",
                "summary": "Customer is unhappy with the service they received.",
            })

        # --- Technical intent (default) ------------------------------------
        return json.dumps({
            "category": "technical",
            "urgency": "medium",
            "summary": "Customer is reporting a product or technical issue.",
        })


# ---------------------------------------------------------------------------
# HOW TO GO LIVE
# ---------------------------------------------------------------------------
# Replace the body of `generate_response` with a real call, for example:
#
#     from anthropic import Anthropic
#     client = Anthropic()  # reads ANTHROPIC_API_KEY from the environment
#
#     def generate_response(self, prompt: str) -> str:
#         msg = client.messages.create(
#             model="<current-model-id>",   # check the provider docs
#             max_tokens=512,
#             messages=[{"role": "user", "content": prompt}],
#         )
#         return msg.content[0].text
#
# Nothing else in the project needs to change.
