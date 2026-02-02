"""
Trustworthy AI Validator Example - LangGraph pattern for content verification.

Demonstrates:
- Validator node that checks LLM output before returning
- Conditional routing: pass -> output, fail -> retry
- Placeholder for phone, citation, source verification

Usage:
    uv run python slides/validator_example.py
"""

from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph


class AgentState(TypedDict):
    """State passed through the graph."""
    messages: list
    response: str
    verified: bool
    fail_reason: str | None


def llm_node(state: AgentState) -> dict:
    """Simulated LLM response (replace with real ChatOllama/ChatOpenAI)."""
    # In production: llm.invoke(state["messages"])
    return {"response": "Sample output with claim: 555-123-4567 is the contact."}


def validator_node(state: AgentState) -> dict:
    """
    Validator: check response before passing to user.
    - Format checks (e.g., phone E.164)
    - Source grounding (citations exist)
    - Policy (no PII leakage)
    """
    response = state.get("response", "")
    verified = True
    fail_reason = None

    # Example: simple phone pattern check (E.164 would need libphonenumber)
    if "555-" in response and "555-123" not in response:
        # Placeholder: reject if format looks wrong
        verified = False
        fail_reason = "phone_format"

    # Placeholder: citation verification (would call legal DB API)
    # if "citation" in response and not legal_db.verify(response):
    #     verified = False
    #     fail_reason = "unverified_citation"

    return {"verified": verified, "fail_reason": fail_reason}


def route_after_validator(
    state: AgentState,
) -> Literal["output", "retry"]:
    """Route based on validator result."""
    if state.get("verified", False):
        return "output"
    return "retry"


def output_node(state: AgentState) -> dict:
    """Final output - only reached when verified."""
    return {"response": state["response"], "verified": True}


def retry_node(state: AgentState) -> dict:
    """Retry path - could re-prompt with correction instructions."""
    return {"response": f"[RETRY] Previous failed: {state.get('fail_reason', 'unknown')}"}


def build_validator_graph():
    """Build graph with validator in the critical path."""
    graph = StateGraph(AgentState)

    graph.add_node("llm", llm_node)
    graph.add_node("validator", validator_node)
    graph.add_node("output", output_node)
    graph.add_node("retry", retry_node)

    graph.add_edge(START, "llm")
    graph.add_edge("llm", "validator")
    graph.add_conditional_edges(
        "validator",
        route_after_validator,
        {"output": "output", "retry": "retry"},
    )
    graph.add_edge("output", END)
    graph.add_edge("retry", END)  # Or: retry -> llm for actual retry loop

    return graph.compile()


if __name__ == "__main__":
    g = build_validator_graph()
    result = g.invoke({"messages": [], "response": "", "verified": False, "fail_reason": None})
    print("Result:", result)
