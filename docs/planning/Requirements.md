# Software Requirements Specification (SRS)

# Customer Intelligence Platform

## Project Overview

The Customer Intelligence Platform is a full-stack web application designed for small business owners to manage customer information, analyze purchasing behavior, and generate actionable customer insights using RFM analysis and K-Means clustering.

---

# Functional Requirements

The system shall allow users to:

### Authentication
- Register an account
- Login securely
- Logout securely

### Project Management
- Create projects
- Edit project information
- Delete projects
- View all projects

### Customer Management
- Add customers
- Edit customer details
- Delete customers
- Search customers

### Transaction Management
- Record customer purchases
- Edit transactions
- Delete transactions
- View purchase history

### Analytics
- Calculate Recency, Frequency, and Monetary values
- Perform K-Means clustering
- Display customer segments
- Display business insights
- Show revenue distribution
- Generate recommendations for each customer segment

---

# Non-Functional Requirements

The system should:

- Be responsive across desktop and mobile devices.
- Use secure authentication.
- Store data in PostgreSQL.
- Process analytics efficiently.
- Follow REST API principles.
- Support future scalability.

---

# Technologies

Frontend:
- React
- Tailwind CSS

Backend:
- FastAPI

Database:
- PostgreSQL (Supabase)

Machine Learning:
- Scikit-learn
- Pandas
- NumPy