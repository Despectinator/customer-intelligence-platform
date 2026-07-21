# Database Schema

## Overview

The Customer Intelligence Platform uses PostgreSQL (Supabase) as its primary relational database. Authentication is handled by Supabase Auth, while the application stores project, customer, and transaction data. Customer segments are generated dynamically using RFM analysis and K-Means clustering instead of being permanently stored.

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

Stores customer purchase history.

| Column | Data Type | Constraints | Description |
|---------|-----------|-------------|-------------|
| id | UUID | Primary Key | Unique transaction identifier |
| customer_id | UUID | Foreign Key | References Customers |
| order_date | DATE | NOT NULL | Purchase date |
| order_amount | DECIMAL | NOT NULL | Purchase amount |
| payment_method | TEXT | Nullable | Payment method |
| created_at | TIMESTAMP | Default CURRENT_TIMESTAMP | Record creation date |

---

## Relationships

User (Supabase Auth)
    │
    └── One User → Many Projects

Project
    │
    └── One Project → Many Customers

Customer
    │
    └── One Customer → Many Transactions

---

## Derived Data

The following information is **not stored** in the database. Instead, it is calculated dynamically whenever required:

- Recency (Days since last purchase)
- Frequency (Number of purchases)
- Monetary (Total customer spending)
- Customer Segment
- Business Recommendations

This design minimizes redundant data and ensures customer insights always reflect the latest transaction history.