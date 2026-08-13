"""
K-Means clustering over RFM feature vectors. Trains a fresh model on the
current project's customer RFM data and returns a raw cluster_number per
customer. Clustering is run per-project, not globally — what counts as
"high value" looks different store to store.
"""
import uuid
from typing import Optional
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from app.core.config import settings

MIN_CUSTOMERS_FOR_SEGMENTATION = 4


def cluster_customers(
    rfm_records: list[dict],
    n_clusters: Optional[int] = None,
    random_state: int = 42,
) -> dict[uuid.UUID, int]:
    """
    rfm_records: output of app.ml.rfm.calculate_project_rfm()

    n_clusters defaults to settings.KMEANS_N_CLUSTERS (configurable via
    the KMEANS_N_CLUSTERS env var) rather than a hardcoded literal, since
    the number of segments is a business decision, not an implementation
    detail. Callers (tests, or future per-project overrides) can still
    pass an explicit value.

    Returns {customer_id: cluster_number}. Returns an empty dict only when
    there are fewer than 2 customers with transaction history — clustering
    is meaningless with 0 or 1 points. Otherwise, if there are fewer
    customers than the requested cluster count (e.g. a new project with 3
    customers but KMEANS_N_CLUSTERS=4), n_clusters is clamped down to the
    number of available customers rather than refusing to segment at all.
    A small project still gets a meaningful (if coarser) segmentation
    instead of an empty result — important for demos and early-stage
    projects, where refusing to show any segments at all would look like
    a broken feature rather than "not enough data yet."

    Features are standardized before clustering (StandardScaler) so that
    monetary_value, which is typically on a much larger numeric scale than
    recency_days or frequency_count, doesn't dominate the distance
    calculation just because of its units.
    """
    if n_clusters is None:
        n_clusters = settings.KMEANS_N_CLUSTERS

    if len(rfm_records) < MIN_CUSTOMERS_FOR_SEGMENTATION:
        return {}

    n_clusters = min(n_clusters, len(rfm_records))

    features = np.array(
        [
            [r["recency_days"], r["frequency_count"], r["monetary_value"]]
            for r in rfm_records
        ]
    )

    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)

    model = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    cluster_labels = model.fit_predict(scaled_features)

    return {
        record["customer_id"]: int(label)
        for record, label in zip(rfm_records, cluster_labels)
    }
