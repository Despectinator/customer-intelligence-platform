"""
Per-segment business recommendations. This is the code-level lookup
described in docs/architecture/Database-Schema.md — recommendation text is
generated here from a segment_name, never stored per customer row, since
it's identical for every customer in a given segment.
"""
from typing import Optional

SEGMENT_RECOMMENDATIONS: dict[str, str] = {
    "Loyal High-Value": (
        "Prioritize retention: exclusive offers, early access to new products, "
        "and loyalty rewards. These customers drive disproportionate revenue."
    ),
    "At Risk": (
        "Send a targeted re-engagement campaign with a personalized discount "
        "before they churn — recency is climbing but they were previously active."
    ),
    "New": (
        "Nurture with onboarding content and a follow-up offer after their "
        "first purchase to encourage a second one."
    ),
    "Lost": (
        "Low-cost win-back campaign only; consider deprioritizing further "
        "spend on this group if there's no response."
    ),
}

DEFAULT_RECOMMENDATION = "No specific recommendation available for this segment yet."


def get_recommendation(segment_name: Optional[str]) -> str:
    """
    Looks up the recommended action for a given segment name. Returns a
    safe default for unrecognized or missing segment names, rather than
    raising, since this is display text — not a validation gate.
    """
    if not segment_name:
        return DEFAULT_RECOMMENDATION
    return SEGMENT_RECOMMENDATIONS.get(segment_name, DEFAULT_RECOMMENDATION)
