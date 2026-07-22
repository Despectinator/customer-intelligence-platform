# Backend

FastAPI backend for the Customer Intelligence Platform.

## Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── routes/          # Route definitions (thin controllers)
│   │   └── dependencies.py  # Shared FastAPI dependencies (DB session, current user)
│   ├── core/
│   │   ├── config.py        # Environment/config loading
│   │   └── security.py      # Supabase JWT verification
│   ├── database/
│   │   ├── database.py      # SQLAlchemy engine/session setup
│   │   └── models/          # SQLAlchemy models, one file per table
│   ├── schemas/              # Pydantic request/response models
│   ├── services/             # Business logic, separated from route handlers
│   ├── utils/                 # Shared helper functions
│   └── main.py                # FastAPI app entrypoint
├── tests/
├── get_test_token.py          # Dev helper: get a login token before the frontend exists
├── .env.example
└── requirements.txt
```

**Layering convention:** routes call services; services call the database via SQLAlchemy models. Routes should stay thin — no direct DB queries in route handlers.

## Local setup

```bash
python -m venv venv
venv\Scripts\activate        # Windows PowerShell; use `source venv/bin/activate` on Mac/Linux
pip install -r requirements.txt
cp .env.example .env         # fill in your Supabase credentials
```

## Run

```bash
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the interactive Swagger UI.

## Get a test login token

Since the frontend doesn't exist yet, use this to authenticate manually against Swagger:

```bash
python get_test_token.py you@example.com yourpassword123
```

Paste the printed token into Swagger's **Authorize** button as `Bearer <token>`.

## Run tests

```bash
pytest
```
