import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")  # secret key — backend only
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    def validate(self) -> None:
        missing = [
            name
            for name, value in [
                ("SUPABASE_URL", self.SUPABASE_URL),
                ("SUPABASE_KEY", self.SUPABASE_KEY),
                ("DATABASE_URL", self.DATABASE_URL),
            ]
            if not value
        ]
        if missing:
            raise RuntimeError(
                f"Missing required environment variables: {', '.join(missing)}. "
                "Copy backend/.env.example to backend/.env and fill it in."
            )


settings = Settings()
