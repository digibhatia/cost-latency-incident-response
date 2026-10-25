"""
Model routing / tiering — Module 6.

Production teams typically do this with LiteLLM's router (model lists,
fallback chains, load balancing across providers/keys). This file is a
small, dependency-free stand-in that implements the same DECISION the
router makes — which tier a request belongs in — so the logic is fully
visible for the lab. Swapping this for a real LiteLLM Router config is a
drop-in change: route_request() stays the call site, only its internals
change.

Two tiers:
  - "light"  (gpt-4o-mini) for single-tool-call, low-ambiguity requests
  - "heavy"  (gpt-4o)      for anything that needs multi-step reasoning
               over several pieces of evidence (and for the SAR-drafting
               sub-agent, which must sound reliably professional)
"""

from dataclasses import dataclass

LIGHT_TIER_MODEL = "gpt-4o-mini"
HEAVY_TIER_MODEL = "gpt-4o"


@dataclass
class RoutingDecision:
    model: str
    tier: str
    reason: str


def route_request(task_kind: str, complexity_hint: str = "normal") -> RoutingDecision:
    """
    task_kind: "tool_loop" (the main investigation loop) or "sub_agent" (SAR drafting)
    complexity_hint: "normal" or "high" — callers can pass "high" when they
    already know a case is unusually large (e.g. many transactions, several
    watchlist hits) to force the heavy tier even for the tool loop.
    """
    if task_kind == "sub_agent":
        return RoutingDecision(
            model=HEAVY_TIER_MODEL, tier="heavy",
            reason="SAR narratives are reviewer-facing and must be reliably well-formed",
        )
    if complexity_hint == "high":
        return RoutingDecision(
            model=HEAVY_TIER_MODEL, tier="heavy",
            reason="caller flagged high complexity (large transaction set / multiple watchlist hits)",
        )
    return RoutingDecision(
        model=LIGHT_TIER_MODEL, tier="light",
        reason="standard tool-calling turn, no complexity signal raised",
    )
