import uuid
from app.ml.clustering import cluster_customers


def make_record(recency, frequency, monetary):
    return {
        "customer_id": uuid.uuid4(),
        "recency_days": recency,
        "frequency_count": frequency,
        "monetary_value": monetary,
    }


def test_returns_empty_for_zero_records():
    assert cluster_customers([], n_clusters=4) == {}


def test_returns_empty_for_a_single_record():
    # Clustering a single point is meaningless regardless of n_clusters.
    records = [make_record(5, 2, 100)]
    assert cluster_customers(records, n_clusters=4) == {}


def test_clamps_n_clusters_to_available_customers():
    # Requesting 4 clusters with only 3 customers should still segment
    # them (into at most 3 groups), not return nothing. Important for
    # small/early-stage projects and live demos.
    records = [make_record(i, i, i * 10) for i in range(1, 4)]
    result = cluster_customers(records, n_clusters=4)

    assert len(result) == 3
    assert len(set(result.values())) <= 3


def test_returns_one_cluster_assignment_per_customer():
    records = [make_record(i, i, i * 10) for i in range(1, 6)]
    result = cluster_customers(records, n_clusters=2)
    assert len(result) == len(records)
    for record in records:
        assert record["customer_id"] in result


def test_distinct_groups_are_separated_into_different_clusters():
    # Two tight, well-separated groups -> K-Means with n_clusters=2 should
    # put each group entirely in its own cluster.
    group_a = [make_record(2, 20, 1500) for _ in range(4)]
    group_b = [make_record(300, 1, 20) for _ in range(4)]
    records = group_a + group_b

    result = cluster_customers(records, n_clusters=2)

    group_a_clusters = {result[r["customer_id"]] for r in group_a}
    group_b_clusters = {result[r["customer_id"]] for r in group_b}

    assert len(group_a_clusters) == 1
    assert len(group_b_clusters) == 1
    assert group_a_clusters != group_b_clusters
