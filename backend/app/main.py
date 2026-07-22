from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router

# Note: tables are created by database/schema.sql (run directly in the
# Supabase SQL editor), not by SQLAlchemy at startup. This keeps a single
# source of truth for the schema instead of two competing definitions.

app = FastAPI(title="Customer Intelligence Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten to your Vercel domain before final submission
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(api_router)
