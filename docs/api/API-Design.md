# REST API Design

## Overview

The backend follows RESTful API principles. All requests are handled by FastAPI, while authentication is managed through Supabase.

---

# Authentication

| Method | Endpoint | Description |
|---------|----------|-------------|
| POST | /auth/register | Register a new user |
| POST | /auth/login | Authenticate user |
| POST | /auth/logout | Logout current user |

---

# Projects

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | /projects | Retrieve all projects |
| POST | /projects | Create a new project |
| GET | /projects/{id} | Retrieve project details |
| PUT | /projects/{id} | Update project |
| DELETE | /projects/{id} | Delete project |

---

# Customers

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | /customers | Retrieve customers |
| POST | /customers | Create customer |
| GET | /customers/{id} | Retrieve customer |
| PUT | /customers/{id} | Update customer |
| DELETE | /customers/{id} | Delete customer |

---

# Transactions

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | /transactions | Retrieve transactions |
| POST | /transactions | Add transaction |
| GET | /transactions/{id} | Retrieve transaction |
| PUT | /transactions/{id} | Update transaction |
| DELETE | /transactions/{id} | Delete transaction |

---

# Analytics

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | /analytics/rfm | Calculate RFM metrics |
| GET | /analytics/segments | Generate customer segments |
| GET | /analytics/dashboard | Retrieve dashboard analytics |

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