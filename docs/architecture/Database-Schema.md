# Database Schema

## Overview

The Customer Intelligence Platform uses PostgreSQL (Supabase) as its primary relational database. Authentication is handled by Supabase Auth.

**Design principle:** Recency, Frequency, and Monetary (RFM) values are **never stored** — they are always calculated on demand from the `Transactions` table. Only the *result* of clustering (the segment assignment) is persisted, because that's the expensive, non-trivial computation worth caching. This keeps the schema normalized and avoids stale RFM data ever drifting out of sync with actual transactions.

---

## Database Tables

### 1. Projects

Stores business projects created by authenticated users.

| Column | Data Type | Constraints | Description |
|---------|-----------|-------------|-------------|
| id | UUID | Primary Key | Unique project identifier |
| user_id | UUID | Foreign Key | References authenticated user |
| name | TEXT | NOT NULL | Project name |
| description | TEXT | Nullable | Project description |
| created_at | TIMESTAMP | Default CURRENT_TIMESTAMP | Creation date |

---

### 2. Customers

Stores customer information for each project.

| Column | Data Type | Constraints | Description |
|---------|-----------|-------------|-------------|
| id | UUID | Primary Key | Unique customer identifier |
| project_id | UUID | Foreign Key | References Projects |
| customer_name | TEXT | NOT NULL | Customer full name |
| email | TEXT | Nullable | Customer email |
| phone | TEXT | Nullable | Customer phone number |
| created_at | TIMESTAMP | Default CURRENT_TIMESTAMP | Record creation date |

---

### 3. Transactions

Stores purchase history per customer. This is the single source of truth RFM is calculated from — never a separate stored value.

| Column | Data Type | Constraints | Description |
|---------|-----------|-------------|-------------|
| id | UUID | Primary Key | Unique transaction identifier |
| customer_id | UUID | Foreign Key | References Customers |
| order_date | DATE | NOT NULL | Date of purchase |
| order_amount | DECIMAL | NOT NULL | Purchase amount |
| payment_method | TEXT | Nullable | Payment method used |
| created_at | TIMESTAMP | Default CURRENT_TIMESTAMP | Record creation date |

---

### 4. Segments

Stores only the **current clustering result** per customer — not the RFM values that produced it. One row per customer, overwritten whenever segmentation is recomputed.

| Column | Data Type | Constraints | Description |
|---------|-----------|-------------|-------------|
| id | UUID | Primary Key | Unique segment record identifier |
| project_id | UUID | Foreign Key | References Projects (denormalized for simpler RLS/queries) |
| customer_id | UUID | Foreign Key, UNIQUE | References Customers (one active segment per customer) |
| cluster_number | INTEGER | Nullable | Raw K-Means cluster label |
| segment_name | TEXT | Nullable | Human-readable label (e.g. "Loyal High-Value") |
| generated_at | TIMESTAMP | Default CURRENT_TIMESTAMP | Time this segment was last computed |

> **Recommendations are not stored per row.** The mapping from `segment_name` to an action recommendation (e.g. "Loyal High-Value" → "prioritize retention offers") lives as a lookup in application code, since it's the same for every customer in a given segment — storing it per row would just duplicate the same string hundreds of times.

---

### 5. Segment_History

Append-only log of segment changes. Powers the real-time migration feed on the dashboard.

| Column | Data Type | Constraints | Description |
|---------|-----------|-------------|-------------|
| id | UUID | Primary Key | Unique history record identifier |
| customer_id | UUID | Foreign Key | References Customers |
| old_segment | TEXT | Nullable | Previous segment name |
| new_segment | TEXT | NOT NULL | New segment name |
| changed_at | TIMESTAMP | Default CURRENT_TIMESTAMP | Time of the change |

---

## Notes

- `users` is not a table in this schema — it is managed by Supabase Auth (`auth.users`) and referenced only by foreign key.
- All tables have Row Level Security enabled so a user can only read/write data belonging to their own projects.
- Any endpoint that needs to *display* RFM numbers (e.g. a customer detail view) computes them at request time with an aggregate query over `Transactions` — it does not read them from a stored column.
