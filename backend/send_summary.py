#!/usr/bin/env python3
"""
CLI entry point to generate and email the daily portfolio visitor summary report.
Usage:
    python send_summary.py
    python send_summary.py --hours 48
    python send_summary.py --dry-run
"""
import argparse
import sys
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database import SessionLocal
from app.visitor_summary import generate_visitor_summary_data, format_visitor_summary_email, send_daily_summary

def main():
    parser = argparse.ArgumentParser(description="Send Daily Portfolio Visitor Summary via Gmail")
    parser.add_argument("--hours", type=int, default=24, help="Reporting window in hours (default: 24)")
    parser.add_argument("--dry-run", action="store_true", help="Print summary to console without sending email")
    args = parser.parse_args()

    with SessionLocal() as db:
        if args.dry_run:
            data = generate_visitor_summary_data(db, hours=args.hours)
            subject, text_body, _ = format_visitor_summary_email(data)
            print("=" * 60)
            print(f"SUBJECT: {subject}")
            print("=" * 60)
            print(text_body)
            print("=" * 60)
            print("[DRY-RUN] Email not sent.")
            return

        print(f"Generating and dispatching visitor summary for past {args.hours} hours...")
        ok, msg, data = send_daily_summary(db, hours=args.hours)
        if ok:
            print(f"✔ Summary sent successfully! ({data['total_visits']} visits, {data['unique_visitors']} unique visitors)")
        else:
            print(f"✖ Failed or simulated: {msg}")

if __name__ == "__main__":
    main()
