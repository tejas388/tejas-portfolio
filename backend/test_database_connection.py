"""
Safe database connection, migration, and CRUD verification script.
Tests active database configured in DATABASE_URL (or defaults to SQLite).
NEVER logs or exposes database passwords or credentials.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

load_dotenv(BASE_DIR / ".env")

from app.database import engine, SessionLocal, DATABASE_URL
from app.migrations import run_migrations
from app.models import Project, Certification, Achievement, ContactMessage, PortfolioVisit
from sqlalchemy import text

def mask_db_url(url: str) -> str:
    """Masks credentials in database URL for safe terminal logging."""
    if "@" in url:
        prefix = url.split("://")[0]
        host_part = url.split("@")[-1]
        return f"{prefix}://*****:*****@{host_part}"
    return url

def main():
    print("=" * 60)
    print("PORTFOLIO DATABASE CONNECTION & MIGRATION VERIFICATION")
    print(f"Target: {mask_db_url(DATABASE_URL)}")
    print(f"Dialect: {engine.dialect.name} (Driver: {engine.dialect.driver})")
    print("=" * 60)

    # 1. Connectivity test
    print("\n[Step 1] Testing basic connectivity...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            assert result == 1
        print("✔ Connection handshake successful (SELECT 1 passed).")
    except Exception as exc:
        print(f"✖ Connection failed: {type(exc).__name__}: {exc}")
        sys.exit(1)

    # 2. Schema creation & migration test
    print("\n[Step 2] Executing schema migrations and default seeding...")
    try:
        with SessionLocal() as db:
            run_migrations(db)
        print("✔ Schema migrations applied cleanly without errors.")
    except Exception as exc:
        print(f"✖ Migration failed: {type(exc).__name__}: {exc}")
        sys.exit(1)

    # 3. Read test
    print("\n[Step 3] Verifying seeded portfolio records...")
    with SessionLocal() as db:
        proj_count = db.query(Project).count()
        cert_count = db.query(Certification).count()
        ach_count = db.query(Achievement).count()
        print(f"✔ Projects table: {proj_count} records (expected >= 3)")
        print(f"✔ Certifications table: {cert_count} records (expected >= 5)")
        print(f"✔ Achievements table: {ach_count} records (expected >= 2)")
        assert proj_count >= 3, "Missing default projects"
        assert cert_count >= 5, "Missing default certifications"
        assert ach_count >= 2, "Missing default achievements"

    # 4. Write & Delete (CRUD) test
    print("\n[Step 4] Testing write and delete operations...")
    with SessionLocal() as db:
        test_contact = ContactMessage(
            name="CRUD Verification Lead",
            email="crud-test@example.com",
            message="Temporary database write verification check.",
            status="test"
        )
        db.add(test_contact)
        db.commit()
        db.refresh(test_contact)
        saved_id = test_contact.id
        print(f"✔ Write successful (created contact record id={saved_id}).")

        # Read back
        fetched = db.query(ContactMessage).filter(ContactMessage.id == saved_id).first()
        assert fetched is not None, "Failed to read back newly created record"
        print("✔ Read-back verified.")

        # Clean up
        db.delete(fetched)
        db.commit()
        print("✔ Cleaned up test record.")

    print("\n" + "=" * 60)
    print("ALL DATABASE CHECKS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    main()
