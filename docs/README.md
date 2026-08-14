# Documentation

Everything here backs a specific decision in the codebase — start with **System Architecture** if you're new to the project.

## Architecture

| Doc | What it covers |
|---|---|
| [System-Architecture.md](./architecture/System-Architecture.md) | Three-tier overview, tech stack, the "live without streaming" analytics flow |
| [ER-Diagram.md](./architecture/ER-Diagram.md) | Entity-relationship diagram for projects, customers, transactions, segments |
| [Database-Schema.md](./architecture/Database-Schema.md) | Table-by-table schema rationale — why RFM is computed, not stored |
| [CSV-Upload-Flow.md](./architecture/CSV-Upload-Flow.md) | Bulk import path: validation, duplicate detection, segment recompute trigger |

## API

| Doc | What it covers |
|---|---|
| [API-Design.md](./api/API-Design.md) | REST endpoint reference — projects, customers, transactions, upload, analytics |

## Planning

| Doc | What it covers |
|---|---|
| [Requirements.md](./planning/Requirements.md) | Original functional requirements |
| [Roadmap.md](./planning/Roadmap.md) | Module-by-module delivery plan |
| [User-Stories.md](./planning/User-Stories.md) | User stories the feature set was designed against |

---

[← Back to project README](../README.md)
