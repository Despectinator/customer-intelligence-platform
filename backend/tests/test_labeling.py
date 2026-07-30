import uuid
from app.ml.labeling import label_clusters


def test_four_archetypes_get_correct_labels():
    champion_id, new_id, at_risk_id, lost_id = [uuid.uuid4() for _ in range(4)]

    rfm_records = [
        {"customer_id": champion_id, "recency_days": 3, "frequency_count": 20, "monetary_value": 1800},
        {"customer_id": new_id, "recency_days": 4, "frequency_count": 1, "monetary_value": 50},
        {"customer_id": at_risk_id, "recency_days": 160, "frequency_count": 18, "monetary_value": 1600},
        {"customer_id": lost_id, "recency_days": 210, "frequency_count": 1, "monetary_value": 40},
    ]
    cluster_assignment = {champion_id: 0, new_id: 1, at_risk_id: 2, lost_id: 3}

    labels = label_clusters(rfm_records, cluster_assignment)

    assert labels[0] == "Loyal High-Value"
    assert labels[1] == "New"
    assert labels[2] == "At Risk"
    assert labels[3] == "Lost"


def test_empty_assignment_returns_empty_labels():
    assert label_clusters([], {}) == {}


def test_labels_are_stable_regardless_of_raw_cluster_index():
    # Same four archetypes, but with scrambled cluster index numbers —
    # labels should be assigned by RFM profile, not by index value.
    champion_id, new_id, at_risk_id, lost_id = [uuid.uuid4() for _ in range(4)]

    rfm_records = [
        {"customer_id": champion_id, "recency_days": 3, "frequency_count": 20, "monetary_value": 1800},
        {"customer_id": new_id, "recency_days": 4, "frequency_count": 1, "monetary_value": 50},
        {"customer_id": at_risk_id, "recency_days": 160, "frequency_count": 18, "monetary_value": 1600},
        {"customer_id": lost_id, "recency_days": 210, "frequency_count": 1, "monetary_value": 40},
    ]
    # Deliberately scrambled index assignment
    cluster_assignment = {champion_id: 3, new_id: 0, at_risk_id: 1, lost_id: 2}

    labels = label_clusters(rfm_records, cluster_assignment)

    assert labels[cluster_assignment[champion_id]] == "Loyal High-Value"
    assert labels[cluster_assignment[new_id]] == "New"
    assert labels[cluster_assignment[at_risk_id]] == "At Risk"
    assert labels[cluster_assignment[lost_id]] == "Lost"
