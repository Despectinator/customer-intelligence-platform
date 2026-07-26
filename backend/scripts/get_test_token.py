"""
Quick helper for local testing, before the frontend login page exists.

Logs in an existing test user against your Supabase project and prints an
access token you can paste into the FastAPI Swagger UI's "Authorize" button
(http://127.0.0.1:8000/docs).

Note: this does NOT create an account. Sign up first via Supabase Auth
(or POST to Supabase's signup endpoint directly) if the account doesn't
exist yet — this script will fail loudly with a traceback if login fails.

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
    except Exception as e:
        print("=" * 60)
        print("LOGIN FAILED")
        print(type(e).__name__)
        print(str(e))
        print("=" * 60)
        raise

    if result.session:
        print("\nAccess token (paste into Swagger's Authorize button as: Bearer <token>):\n")
        print(result.session.access_token)
    else:
        print("\nLogged in, but no session was returned. Check that the account is confirmed.")


if __name__ == "__main__":
    main()
