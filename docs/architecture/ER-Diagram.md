# Entity Relationship Diagram (ERD)

## Overview

The Customer Intelligence Platform follows a relational database design. Authentication is managed by Supabase Auth. RFM values are never stored — only the clustering result (`Segments`) and its change history (`Segment_History`) are persisted.

```mermaid
erDiagram

    USERS ||--o{ PROJECTS : owns
    PROJECTS ||--o{ CUSTOMERS : contains
    PROJECTS ||--o{ SEGMENTS : scopes
    CUSTOMERS ||--o{ TRANSACTIONS : has
    CUSTOMERS ||--|| SEGMENTS : "current segment"
    CUSTOMERS ||--o{ SEGMENT_HISTORY : "migration log"

    USERS {
        uuid id PK
        string email
    }

    PROJECTS {
        uuid id PK
        uuid user_id FK
        string name
        string description
        datetime created_at
    }

    CUSTOMERS {
        uuid id PK
        uuid project_id FK
        string customer_name
        string email
        string phone
        datetime created_at
    }

    TRANSACTIONS {
        uuid id PK
        uuid customer_id FK
        date order_date
        decimal order_amount
        string payment_method
        datetime created_at
    }

    SEGMENTS {
        uuid id PK
        uuid project_id FK
        uuid customer_id FK
        int cluster_number
        string segment_name
        datetime generated_at
    }

    SEGMENT_HISTORY {
        uuid id PK
        uuid customer_id FK
        string old_segment
        string new_segment
        datetime changed_at
    }
```

---

## Relationship Summary

- One authenticated user can own multiple projects.
- One project can contain multiple customers, and scopes its own set of segment records.
- One customer can have multiple transactions — this is the only source RFM values are ever calculated from.
- One customer has exactly one current segment record (1:1), overwritten whenever clustering is recomputed.
- One customer can have multiple segment history entries — an append-only log of every time their segment changed, used to power the real-time migration feed on the dashboard.
