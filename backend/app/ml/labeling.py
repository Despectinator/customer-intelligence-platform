"""
Maps arbitrary K-Means cluster numbers to business segment labels.

K-Means already standardizes the customer-level RFM features before
clustering. This module separately standardizes each cluster's average RFM
profile before ranking clusters, so frequency and monetary value are not
combined in their original units.
"""

import uuid
from statistics import mean, pstdev


def _zscore(value: float, values: list[float]) -> float:
    """Return a population z-score, or zero when all values are equal."""
    deviation = pstdev(values)
    if deviation == 0:
        return 0.0
    return (value - mean(values)) / deviation


def label_clusters(
    rfm_records: list[dict],
    cluster_assignment: dict[uuid.UUID, int],
) -> dict[int, str]:
    """Return ``{cluster_number: business_segment_name}``.

    Recency is directional: a lower value means the customer purchased more
    recently. Frequency and monetary value are standardized across cluster
    profiles before they are combined into a comparable value score.

    Clusters are divided into a more-recent half and an older half. Within
    each half, the highest standardized value profile receives the stronger
    business label:

    - recent + high value -> Loyal High-Value
    - recent + lower value -> New
    - older + high value -> At Risk
    - older + lower value -> Lost
    """
    by_cluster: dict[int, list[dict]] = {}

    for record in rfm_records:
        cluster_number = cluster_assignment.get(record["customer_id"])
        if cluster_number is not None:
            by_cluster.setdefault(cluster_number, []).append(record)

    if not by_cluster:
        return {}

    raw_profiles = {
        cluster_number: {
            "avg_recency": mean(record["recency_days"] for record in records),
            "avg_frequency": mean(
                record["frequency_count"] for record in records
            ),
            "avg_monetary": mean(
                record["monetary_value"] for record in records
            ),
        }
        for cluster_number, records in by_cluster.items()
    }

    recency_values = [profile["avg_recency"] for profile in raw_profiles.values()]
    frequency_values = [
        profile["avg_frequency"] for profile in raw_profiles.values()
    ]
    monetary_values = [
        profile["avg_monetary"] for profile in raw_profiles.values()
    ]

    profiles = {}
    for cluster_number, profile in raw_profiles.items():
        profiles[cluster_number] = {
            # Lower recency is better, so the more recent clusters sort first.
            "activity_score": -_zscore(profile["avg_recency"], recency_values),
            "value_score": (
                _zscore(profile["avg_frequency"], frequency_values)
                + _zscore(profile["avg_monetary"], monetary_values)
            ),
        }

    sorted_by_recency = sorted(
        profiles.items(),
        key=lambda item: item[1]["activity_score"],
        reverse=True,
    )
    midpoint = max(1, len(sorted_by_recency) // 2)
    recent_half = sorted_by_recency[:midpoint]
    older_half = sorted_by_recency[midpoint:]

    labels: dict[int, str] = {}

    if recent_half:
        recent_by_value = sorted(
            recent_half,
            key=lambda item: item[1]["value_score"],
            reverse=True,
        )
        labels[recent_by_value[0][0]] = "Loyal High-Value"
        for cluster_number, _ in recent_by_value[1:]:
            labels[cluster_number] = "New"

    if older_half:
        older_by_value = sorted(
            older_half,
            key=lambda item: item[1]["value_score"],
            reverse=True,
        )
        labels[older_by_value[0][0]] = "At Risk"
        for cluster_number, _ in older_by_value[1:]:
            labels[cluster_number] = "Lost"

    return labels
