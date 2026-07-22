"""
Quick helper for local testing, before the frontend login page exists.

Signs up (or logs in, if the account already exists) a test user against
your Supabase project and prints an access token you can paste into the
FastAPI Swagger UI's "Authorize" button (http://127.0.0.1:8000/docs).

Usage:
    python get_test_token.py you@example.com yourpassword123
"""
import sys
from dotenv import load_dotenv
from supabase import create_client

from app.core.config import settings

load_dotenv()


def main():
    if len(sys.argv) != 3:
        print("Usage: python get_test_token.py <email> <password>")
        sys.exit(1)

    email, password = sys.argv[1], sys.argv[2]
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

    try:
        result = supabase.auth.sign_in_with_password({"email": email, "password": password})
    except Exception:
        print("No existing account found — signing up instead...")
        result = supabase.auth.sign_up({"email": email, "password": password})

    if result.session:
        print("\nAccess token (paste into Swagger's Authorize button as: Bearer <token>):\n")
        print(result.session.access_token)
    else:
        print("\nSigned up. Check your email to confirm the account before logging in again.")


if __name__ == "__main__":
    main()
