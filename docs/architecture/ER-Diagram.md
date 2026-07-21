# Entity Relationship Diagram (ERD)

## Overview

The Customer Intelligence Platform follows a relational database design. Authentication is managed by Supabase Auth, while application-specific data is stored in PostgreSQL.

```mermaid
erDiagram

    USERS ||--o{ PROJECTS : owns
    PROJECTS ||--o{ CUSTOMERS : contains
    CUSTOMERS ||--o{ TRANSACTIONS : has

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
```

---

## Relationship Summary

- One authenticated user can own multiple projects.
- One project can contain multiple customers.
- One customer can have multiple transactions.
- Customer segmentation is calculated dynamically from transaction history using RFM analysis and K-Means clustering.