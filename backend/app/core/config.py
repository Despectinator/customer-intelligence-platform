"""
Application configuration.

Loads environment variables from the .env file and provides
a centralized settings object for the application.
"""

import os
from dotenv import load_dotenv

# Load environment variables from backend/.env
load_dotenv()


class Settings:
    """Application settings."""

    # ==========================
    # Application
    # ==========================
    APP_NAME = os.getenv("APP_NAME", "CustomerLens API")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    # Base URL the app is reachable at — used by scripts (e.g.
    # seed_demo_data.py) that call the API over HTTP rather than
    # importing it directly. Defaults to local dev; override via env var
    # once deployed so the same script works against Render without
    # editing source.
    API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

    # Comma-separated list of origins allowed to call this API from a
    # browser. Defaults cover common local dev ports (Vite, CRA) so
    # frontend work isn't blocked out of the box. Update this once the
    # frontend is deployed (e.g. to your Vercel domain) — do NOT leave
    # this as "*" in production, since that would allow any website to
    # make authenticated requests on a logged-in user's behalf.
    ALLOWED_ORIGINS = [
        origin.strip()
        for origin in os.getenv(
            "ALLOWED_ORIGINS",
            "http://localhost:5173,http://localhost:5174,http://localhost:3000",
        ).split(",")
        if origin.strip()
    ]

    # ==========================
    # Supabase
    # ==========================
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

    # ==========================
    # Database
    # ==========================
    DATABASE_URL = os.getenv("DATABASE_URL", "")

    # ==========================
    # Security
    # ==========================
    SECRET_KEY = os.getenv("SECRET_KEY", "")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )

    # ==========================
    # Analytics / ML
    # ==========================
    # Number of K-Means segments to generate per project. Kept configurable
    # rather than hardcoded in clustering.py, since this is a business
    # tuning knob (how many customer tiers to show), not implementation
    # detail. Matches the 4 documented segment labels (Loyal High-Value,
    # At Risk, New, Lost) by default.
    KMEANS_N_CLUSTERS = int(os.getenv("KMEANS_N_CLUSTERS", "4"))

    def validate(self) -> None:
        """
        Ensure all required environment variables are present.
        """

        required = {
            "SUPABASE_URL": self.SUPABASE_URL,
            "SUPABASE_KEY": self.SUPABASE_KEY,
            "DATABASE_URL": self.DATABASE_URL,
            "SECRET_KEY": self.SECRET_KEY,
        }

        missing = [key for key, value in required.items() if not value]

        if missing:
            raise RuntimeError(
                "Missing required environment variables: "
                + ", ".join(missing)
                + "\nPlease update backend/.env before starting the application."
            )


# Global settings object
settings = Settings()
