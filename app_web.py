"""
app_web.py
----------
Streamlit dashboard. A friendly UI that runs the pipeline step by step so you
can *watch* each agent work -- great for demos and portfolios.

Run locally:
    streamlit run app_web.py
Then open the URL Streamlit prints (usually http://localhost:8501).
"""

from __future__ import annotations
import time

import streamlit as st

from component_classifier import classify_with_self_correction
from component_retriever import ToolRetriever
from component_responder import SupportResponder

st.set_page_config(page_title="AI Support Agent", page_icon="🤖")
st.title("🤖 Customer Support AI Agent")
st.caption("A modular three-agent pipeline: Classifier → Retriever → Responder")

customer_email = st.text_area(
    "Customer message",
    value="I was charged twice on my invoice. Please refund my card!",
    height=150,
)

if st.button("Run pipeline", use_container_width=True):
    st.divider()

    # --- Agent 1: Classifier -------------------------------------------------
    with st.spinner("Agent 1 — Classifier: analysing intent..."):
        time.sleep(0.6)  # purely cosmetic, so each step is visible in the demo
        classification = classify_with_self_correction(customer_email)
    st.success("Agent 1 — Classifier complete")

    col1, col2 = st.columns(2)
    urgency_label = {"high": "🔴 HIGH", "medium": "🟡 MEDIUM", "low": "🟢 LOW"}
    col1.metric("Urgency", urgency_label[classification.urgency])
    col2.metric("Category", classification.category.upper())
    st.info(f"**Summary:** {classification.summary}")

    st.divider()

    # --- Agent 2: Retriever --------------------------------------------------
    with st.spinner("Agent 2 — Retriever: fetching the relevant policy..."):
        time.sleep(0.6)
        policy = ToolRetriever().retrieve_policy(classification.category)
    st.success("Agent 2 — Retriever complete")
    with st.expander("Show retrieved policy"):
        st.code(policy.raw_text, language="text")

    st.divider()

    # --- Agent 3: Responder --------------------------------------------------
    with st.spinner("Agent 3 — Responder: drafting the reply..."):
        time.sleep(0.6)
        draft = SupportResponder().generate_draft(customer_email, classification, policy)
    st.success("Agent 3 — Responder complete")
    st.text_area("Draft reply", value=draft, height=260)
    st.balloons()
