"""
Safe, optional data migration utility: copies local SQLite records to PostgreSQL (Neon).
Leaves local SQLite database completely untouched (read-only source).
Supports --dry-run to preview records before committing to PostgreSQL.
Resets PostgreSQL primary key sequences after migration.
"""
import argparse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

load_dotenv(BASE_DIR / ".env")

import sqlite3
from sqlalchemy import create_engine, text
from app.database import Base, DEFAULT_DB_FILE
from app.models import Project, Certification, Achievement, ContactMessage, PortfolioVisit

def mask_url(url: str) -> str:
    if "@" in url:
        prefix = url.split("://")[0]
        host = url.split("@")[-1]
        return f"{prefix}://*****:*****@{host}"
    return url

def main():
    parser = argparse.ArgumentParser(description="Migrate SQLite data to PostgreSQL (Neon)")
    parser.add_argument("--target-url", type=str, default=os.getenv("TARGET_DATABASE_URL"),
                        help="Target PostgreSQL connection URL (or set TARGET_DATABASE_URL env var)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview migration counts without writing to target database")
    args = parser.parse_args()

    sqlite_path = DEFAULT_DB_FILE
    if not sqlite_path.exists():
        print(f"[Error] Local SQLite database not found at {sqlite_path}")
        sys.exit(1)

    if not args.target_url and not args.dry_run:
        print("[Error] Missing target PostgreSQL URL.")
        print("Usage: python migrate_sqlite_to_postgres.py --target-url 'postgresql://...' [--dry-run]")
        sys.exit(1)

    print("=" * 60)
    print("PORTFOLIO SQLITE TO POSTGRESQL DATA MIGRATION")
    print(f"Source (SQLite): {sqlite_path}")
    if args.target_url:
        print(f"Target (PostgreSQL): {mask_url(args.target_url)}")
    print(f"Dry-run mode: {args.dry_run}")
    print("=" * 60)

    # 1. Read existing SQLite records
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row
    cur = sqlite_conn.cursor()

    cur.execute("SELECT * FROM contact_messages ORDER BY id ASC")
    contacts = [dict(r) for r in cur.fetchall()]

    cur.execute("SELECT * FROM portfolio_visits ORDER BY id ASC")
    visits = [dict(r) for r in cur.fetchall()]

    print(f"\nDiscovered {len(contacts)} contact inquiries and {len(visits)} visitor logs in SQLite.")

    if args.dry_run:
        print("\n[DRY RUN] No changes made to PostgreSQL. Data inspected successfully.")
        sqlite_conn.close()
        return

    # Normalize target URL
    target_url = args.target_url
    if target_url.startswith("postgres://"):
        target_url = target_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif target_url.startswith("postgresql://") and not target_url.startswith("postgresql+"):
        target_url = target_url.replace("postgresql://", "postgresql+psycopg://", 1)

    pg_engine = create_engine(target_url, pool_pre_ping=True)
    Base.metadata.create_all(bind=pg_engine)

    from sqlalchemy.orm import sessionmaker
    PgSession = sessionmaker(bind=pg_engine)

    with PgSession() as pg_db:
        # Import contact messages
        inserted_contacts = 0
        for c in contacts:
            existing = pg_db.query(ContactMessage).filter(ContactMessage.id == c["id"]).first()
            if not existing:
                pg_db.add(ContactMessage(**c))
                inserted_contacts += 1

        # Import visits
        inserted_visits = 0
        for v in visits:
            existing = pg_db.query(PortfolioVisit).filter(PortfolioVisit.id == v["id"]).first()
            if not existing:
                pg_db.add(PortfolioVisit(**v))
                inserted_visits += 1

        pg_db.commit()
        print(f"✔ Transferred {inserted_contacts} contact inquiries.")
        print(f"✔ Transferred {inserted_visits} visitor logs.")

        # Reset sequences in PostgreSQL
        with pg_engine.connect() as conn:
            try:
                conn.execute(text("SELECT setval(pg_get_serial_sequence('contact_messages', 'id'), COALESCE(MAX(id), 1)) FROM contact_messages;"))
                conn.execute(text("SELECT setval(pg_get_serial_sequence('portfolio_visits', 'id'), COALESCE(MAX(id), 1)) FROM portfolio_visits;"))
                conn.commit()
                print("✔ Synchronized PostgreSQL primary key auto-increment sequences.")
            except Exception as seq_err:
                print(f"Note: Sequence sync skipped or not needed: {seq_err}")

    sqlite_conn.close()
    print("\n" + "=" * 60)
    print("MIGRATION COMPLETED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    main()
