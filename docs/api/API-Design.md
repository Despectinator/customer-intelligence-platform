# REST API Design

## Overview

The backend follows RESTful API principles and is implemented with FastAPI.

**Authentication is not part of this API.** Registration, login, logout, and session management are handled entirely by the **Supabase Auth SDK on the frontend** — the React app talks to Supabase directly for these actions. Every protected endpoint listed below expects a Supabase-issued JWT in the `Authorization: Bearer <token>` header, which FastAPI verifies before processing the request.

---

# Projects

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | /projects | Retrieve all projects for the current user |
| POST | /projects | Create a new project |
| GET | /projects/{id} | Retrieve project details |
| PUT | /projects/{id} | Update project |
| DELETE | /projects/{id} | Delete project |

---

# Customers

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | /projects/{project_id}/customers | Retrieve customers in a project (supports search/filter query params) |
| POST | /projects/{project_id}/customers | Create customer |
| GET | /customers/{id} | Retrieve customer, including live-computed RFM values and current segment |
| PUT | /customers/{id} | Update customer |
| DELETE | /customers/{id} | Delete customer |

---

# Transactions

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | /customers/{id}/transactions | Retrieve a customer's transactions |
| POST | /customers/{id}/transactions | Add transaction |
| PUT | /transactions/{id} | Update transaction |
| DELETE | /transactions/{id} | Delete transaction |
| POST | /projects/{project_id}/transactions/upload-csv | Bulk-import transactions from CSV |

> Any create/update/delete above triggers the analytics flow: recalculate RFM, re-run K-Means, and update `Segments`/`Segment_History` if the result changed.

---

# Segments & Analytics

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | /projects/{project_id}/segments | All customers in the project, grouped by current segment |
| GET | /projects/{project_id}/segments/summary | Segment counts and revenue % (for dashboard cards) |
| GET | /customers/{id}/segment | Current segment name + recommendation for one customer (recommendation resolved from a code-level lookup, not stored) |
| POST | /projects/{project_id}/segments/recompute | Manually trigger a full re-cluster (e.g. after bulk CSV import) |
| GET | /projects/{project_id}/dashboard/overview | Total customers, total revenue, segment breakdown |
| GET | /projects/{project_id}/dashboard/migrations | Recent segment changes, pulled from Segment_History |

---

## Response Format

Successful responses:

```json
{
  "success": true,
  "data": {}
}
```

Error responses:

```json
{
  "success": false,
  "message": "Error description"
}
```
