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