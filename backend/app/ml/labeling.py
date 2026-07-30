"""
Maps raw K-Means cluster numbers to human-readable segment_name labels
(e.g. "Loyal High-Value", "At Risk", "New", "Lost"). Cluster numbers from
K-Means are arbitrary and unordered across runs — cluster "2" today might
be cluster "0" tomorrow on the same data — so labels are assigned by
ranking each cluster's average RFM profile, never by raw index.

Rule: split clusters into the more-recent half and the less-recent half
by average recency. Within each half, the cluster with the higher average
frequency + monetary is the "better" one:
  - recent + high value   -> Loyal High-Value
  - recent + lower value  -> New
  - not recent + higher value (used to buy a lot, went quiet) -> At Risk
  - not recent + lower value (barely bought, long gone) -> Lost
"""
import uuid
from statistics import mean


def label_clusters(
    rfm_records: list[dict],
    cluster_assignment: dict[uuid.UUID, int],
) -> dict[int, str]:
    """
    rfm_records: output of calculate_project_rfm()
    cluster_assignment: output of cluster_customers() -> {customer_id: cluster_number}

    Returns {cluster_number: segment_name}. Returns an empty dict if
    cluster_assignment is empty (e.g. not enough customers to cluster).
    """
    by_cluster: dict[int, list[dict]] = {}
    for record in rfm_records:
        cluster_number = cluster_assignment.get(record["customer_id"])
        if cluster_number is None:
            continue
        by_cluster.setdefault(cluster_number, []).append(record)

    if not by_cluster:
        return {}

    profiles = {
        cluster_number: {
            "avg_recency": mean(r["recency_days"] for r in records),
            "avg_value": mean(r["frequency_count"] for r in records) + mean(r["monetary_value"] for r in records),
        }
        for cluster_number, records in by_cluster.items()
    }

    sorted_by_recency = sorted(profiles.items(), key=lambda kv: kv[1]["avg_recency"])
    midpoint = max(1, len(sorted_by_recency) // 2)
    recent_half = sorted_by_recency[:midpoint]
    older_half = sorted_by_recency[midpoint:]

    labels: dict[int, str] = {}

    if recent_half:
        recent_by_value = sorted(recent_half, key=lambda kv: kv[1]["avg_value"], reverse=True)
        labels[recent_by_value[0][0]] = "Loyal High-Value"
        for cluster_number, _ in recent_by_value[1:]:
            labels[cluster_number] = "New"

    if older_half:
        older_by_value = sorted(older_half, key=lambda kv: kv[1]["avg_value"], reverse=True)
        labels[older_by_value[0][0]] = "At Risk"
        for cluster_number, _ in older_by_value[1:]:
            labels[cluster_number] = "Lost"

    return labels
