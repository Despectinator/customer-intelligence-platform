"""
Populates a demo project with a handful of customers and varied
transactions, triggers a recompute, and prints the resulting
segments/summary/dashboard/migrations — so you can verify the entire
analytics pipeline in one command instead of clicking through Swagger.

Requires your FastAPI server to already be running (uvicorn app.main:app
--reload) and reachable at settings.API_BASE_URL (defaults to
http://127.0.0.1:8000; override via the API_BASE_URL env var, e.g. once
deployed to Render).

This script does NOT create accounts — it only logs in. If the account
doesn't exist yet, create it first via the Supabase dashboard
(Authentication > Users > Add user), then re-run this script. This keeps
behavior predictable and avoids surprises if email confirmation is
enabled on your Supabase project.

Usage:
    python -m scripts.seed_demo_data you@example.com yourpassword123

By design, the customer profiles below are deliberately spread across all
four segment archetypes (frequent big spender, occasional buyer, big
spender who stopped buying, one-time buyer long ago) rather than random —
this gives K-Means something meaningful to actually separate, instead of
one big blob.
"""
import sys
from datetime import date, timedelta

import httpx
from supabase import create_client

from app.core.config import settings

CUSTOMERS = [
    ("Ali", "Khan", "ali@example.com", [(2, 500), (10, 700), (25, 900)]),
    ("Ahmed", "Raza", "ahmed@example.com", [(5, 2000), (40, 1800)]),
    ("Sara", "Malik", "sara@example.com", [(3, 150)]),
    ("Bilal", "Hussain", "bilal@example.com", [(150, 4000), (170, 5000), (190, 3500)]),
    ("Zara", "Ahmed", "zara@example.com", [(220, 80)]),
]


def get_token(email: str, password: str) -> str:
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    try:
        result = supabase.auth.sign_in_with_password({"email": email, "password": password})
    except Exception:
        print(
            f"Login failed for {email}.\n"
            "This script does not create accounts. Create it first via the "
            "Supabase dashboard (Authentication > Users > Add user), then "
            "re-run this script."
        )
        sys.exit(1)
    if not result.session:
        print("Login succeeded but no session was returned. Check that the account is confirmed.")
        sys.exit(1)
    return result.session.access_token


def print_table(title, rows, columns):
    print(f"\n{title}")
    print("-" * 100)
    if not rows:
        print("  (empty)")
        return
    header = "".join(f"{col:<25}" for col in columns)
    print(header)
    for row in rows:
        print("".join(f"{str(row.get(col, '')):<25}" for col in columns))


def main():
    if len(sys.argv) != 3:
        print("Usage: python -m scripts.seed_demo_data <email> <password>")
        sys.exit(1)

    email, password = sys.argv[1], sys.argv[2]
    token = get_token(email, password)
    headers = {"Authorization": f"Bearer {token}"}

    with httpx.Client(base_url=settings.API_BASE_URL, headers=headers, timeout=10.0) as client:
        print("Creating project...")
        project_resp = client.post(
            "/projects",
            json={"name": "Demo Store", "description": "Seeded demo data"},
        )
        project_resp.raise_for_status()
        project = project_resp.json()
        project_id = project["id"]
        print(f"  Created: {project['name']} ({project_id})")

        print("\nCreating customers and transactions...")
        customer_names_by_id = {}

        for first_name, last_name, email_addr, transactions in CUSTOMERS:
            customer_resp = client.post(
                f"/projects/{project_id}/customers",
                json={
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email_addr,
                    "phone": "03001234567",
                    "company": "Demo Co",
                },
            )
            customer_resp.raise_for_status()
            customer = customer_resp.json()
            customer_id = customer["id"]
            customer_names_by_id[customer_id] = f"{first_name} {last_name}"
            print(f"  {first_name} {last_name} ({customer_id})")

            for days_ago, amount in transactions:
                order_date = (date.today() - timedelta(days=days_ago)).isoformat()
                txn_resp = client.post(
                    f"/customers/{customer_id}/transactions",
                    json={
                        "order_date": order_date,
                        "order_amount": amount,
                        "payment_method": "card",
                    },
                )
                txn_resp.raise_for_status()
                print(f"    {order_date} - ${amount}")

        print("\nRunning recompute...")
        recompute_resp = client.post(f"/projects/{project_id}/segments/recompute")
        recompute_resp.raise_for_status()
        segments = recompute_resp.json()
        for seg in segments:
            seg["customer_name"] = customer_names_by_id.get(seg["customer_id"], seg["customer_id"])
        print_table(
            "Segments",
            segments,
            ["customer_name", "segment_name", "recommendation"],
        )

        print("\nFetching dashboard...")

        summary_resp = client.get(f"/projects/{project_id}/segments/summary")
        summary_resp.raise_for_status()
        print_table(
            "Segment Summary",
            summary_resp.json(),
            ["segment_name", "customer_count", "revenue_total", "revenue_percentage"],
        )

        overview_resp = client.get(f"/projects/{project_id}/dashboard/overview")
        overview_resp.raise_for_status()
        overview = overview_resp.json()
        print(f"\nDashboard Overview")
        print("-" * 100)
        print(f"  Total customers: {overview['total_customers']}")
        print(f"  Total revenue:   ${overview['total_revenue']}")

        migrations_resp = client.get(f"/projects/{project_id}/dashboard/migrations")
        migrations_resp.raise_for_status()
        migrations = migrations_resp.json()
        for m in migrations:
            m["customer_name"] = customer_names_by_id.get(m["customer_id"], m["customer_id"])
        print_table(
            "Recent Migrations",
            migrations,
            ["customer_name", "old_segment", "new_segment", "changed_at"],
        )

        print(f"\nDone. Project ID for further testing: {project_id}")


if __name__ == "__main__":
    main()
