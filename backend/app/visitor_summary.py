"""
Visitor tracking analytics and daily Gmail summary reporter for Tejas CK Portfolio.
Computes non-invasive aggregate metrics: visit counts, unique sessions,
device breakdown (desktop vs mobile vs tablet), and period-over-period comparison.
"""
import logging
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from typing import Dict, Any, Tuple
from sqlalchemy import func
from sqlalchemy.orm import Session
from .models import PortfolioVisit
from .email_service import send_email_smtp, get_smtp_config

logger = logging.getLogger("portfolio.analytics")

IST_TZ = ZoneInfo("Asia/Kolkata")

def generate_visitor_summary_data(db: Session, hours: int = 24) -> Dict[str, Any]:
    """
    Aggregates anonymous visitor telemetry over the specified reporting window (default: 24h)
    and compares with the immediately preceding window.
    """
    now = datetime.now(timezone.utc)
    current_start = now - timedelta(hours=hours)
    prev_start = current_start - timedelta(hours=hours)

    # 1. Current window metrics
    current_visits_query = db.query(PortfolioVisit).filter(PortfolioVisit.created_at >= current_start)
    total_visits = current_visits_query.count()

    unique_visitors = db.query(func.count(func.distinct(PortfolioVisit.visitor_id))).filter(
        PortfolioVisit.created_at >= current_start
    ).scalar() or 0

    # Active sessions: count distinct session_id, falling back to visitor_id if session_id is None
    session_expr = func.coalesce(PortfolioVisit.session_id, PortfolioVisit.visitor_id)
    unique_sessions = db.query(func.count(func.distinct(session_expr))).filter(
        PortfolioVisit.created_at >= current_start
    ).scalar() or 0

    # Device breakdown (defaults any null/unassigned legacy records to "desktop")
    device_expr = func.coalesce(PortfolioVisit.device_category, "desktop")
    device_rows = (
        db.query(device_expr, func.count(PortfolioVisit.id))
        .filter(PortfolioVisit.created_at >= current_start)
        .group_by(device_expr)
        .all()
    )
    device_breakdown = {"desktop": 0, "mobile": 0, "tablet": 0, "unknown": 0}
    for dev, cnt in device_rows:
        dev_key = (dev or "desktop").lower()
        if dev_key in device_breakdown:
            device_breakdown[dev_key] += cnt
        else:
            device_breakdown["unknown"] += cnt

    # Top pages
    page_rows = (
        db.query(PortfolioVisit.page_path, func.count(PortfolioVisit.id))
        .filter(PortfolioVisit.created_at >= current_start)
        .group_by(PortfolioVisit.page_path)
        .order_by(func.count(PortfolioVisit.id).desc())
        .limit(5)
        .all()
    )
    top_pages = [{"path": p, "views": c} for p, c in page_rows]

    # Top referrers
    ref_rows = (
        db.query(PortfolioVisit.referrer, func.count(PortfolioVisit.id))
        .filter(PortfolioVisit.created_at >= current_start, PortfolioVisit.referrer.isnot(None))
        .group_by(PortfolioVisit.referrer)
        .order_by(func.count(PortfolioVisit.id).desc())
        .limit(5)
        .all()
    )
    top_referrers = [{"referrer": r, "count": c} for r, c in ref_rows]

    # 2. Previous window metrics for comparison
    prev_total_visits = db.query(PortfolioVisit).filter(
        PortfolioVisit.created_at >= prev_start,
        PortfolioVisit.created_at < current_start
    ).count()

    prev_unique_visitors = db.query(func.count(func.distinct(PortfolioVisit.visitor_id))).filter(
        PortfolioVisit.created_at >= prev_start,
        PortfolioVisit.created_at < current_start
    ).scalar() or 0

    now_ist = now.astimezone(IST_TZ)
    current_start_ist = current_start.astimezone(IST_TZ)

    return {
        "report_generated_at": now_ist.strftime("%Y-%m-%d %I:%M:%S %p IST"),
        "period_hours": hours,
        "current_start": current_start_ist.strftime("%Y-%m-%d %I:%M %p IST"),
        "current_end": now_ist.strftime("%Y-%m-%d %I:%M %p IST"),
        "total_visits": total_visits,
        "unique_visitors": unique_visitors,
        "unique_sessions": unique_sessions,
        "device_breakdown": device_breakdown,
        "top_pages": top_pages,
        "top_referrers": top_referrers,
        "prev_total_visits": prev_total_visits,
        "prev_unique_visitors": prev_unique_visitors,
    }

def format_visitor_summary_email(summary: Dict[str, Any]) -> Tuple[str, str, str]:
    """
    Formats the summary report into email subject, plain text body, and responsive HTML body.
    Displays all timestamps explicitly in Indian Standard Time (IST).
    """
    date_label = datetime.now(timezone.utc).astimezone(IST_TZ).strftime("%Y-%m-%d")
    subject = f"Daily Portfolio Visitor Summary (IST): {date_label}"

    tot = summary["total_visits"]
    uniq = summary["unique_visitors"]
    sess = summary["unique_sessions"]
    dev = summary["device_breakdown"]
    prev_tot = summary["prev_total_visits"]

    diff_visits = tot - prev_tot
    trend = f"+{diff_visits}" if diff_visits > 0 else str(diff_visits)

    text_body = f"""Daily Portfolio Visitor Summary (IST) ({summary['period_hours']}h)
Generated: {summary['report_generated_at']}
Reporting Window (IST): {summary['current_start']} to {summary['current_end']}

OVERVIEW METRICS
------------------------------------------------------------
Total Recorded Visits:   {tot} ({trend} vs previous {summary['period_hours']}h)
Unique Visitors:         {uniq}
Unique Active Sessions:  {sess}
Prior Period Visits:     {prev_tot}

DEVICE BREAKDOWN
------------------------------------------------------------
Desktop:                 {dev['desktop']}
Mobile:                  {dev['mobile']}
Tablet:                  {dev['tablet']}
Other/Unknown:           {dev['unknown']}

TOP VISITED PATHS
------------------------------------------------------------
"""
    if summary["top_pages"]:
        for p in summary["top_pages"]:
            text_body += f"- {p['path']}: {p['views']} views\n"
    else:
        text_body += "- No page views recorded in this period.\n"

    text_body += "\nTOP REFERRERS\n------------------------------------------------------------\n"
    if summary["top_referrers"]:
        for r in summary["top_referrers"]:
            text_body += f"- {r['referrer']}: {r['count']} visits\n"
    else:
        text_body += "- Direct traffic or referrer header omitted by browser.\n"

    text_body += """
------------------------------------------------------------
Privacy Note:
All metrics are aggregated anonymously. No IP addresses, device serials,
or personally identifying details are stored in your portfolio database.
"""

    pages_html = "".join([f"<tr><td style='padding: 6px 12px; border-bottom: 1px solid #292b32;'><code>{p['path']}</code></td><td style='padding: 6px 12px; text-align: right; border-bottom: 1px solid #292b32; color: #ff454b;'><strong>{p['views']}</strong></td></tr>" for p in summary["top_pages"]]) or "<tr><td colspan='2' style='padding: 8px 12px; color: #888c96;'>No page views recorded in this period.</td></tr>"

    html_body = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: #0f1012; color: #f5f5f7; margin: 0; padding: 24px; }}
    .card {{ max-width: 600px; margin: 0 auto; background: #151619; border: 1px solid #292b32; border-radius: 10px; padding: 28px; }}
    .badge {{ display: inline-block; padding: 4px 10px; background: rgba(255, 69, 75, 0.12); color: #ff454b; font-size: 11px; font-weight: 700; letter-spacing: 0.08em; border-radius: 4px; text-transform: uppercase; margin-bottom: 12px; }}
    h2 {{ color: #ffffff; margin-top: 0; font-size: 20px; }}
    .grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin: 20px 0; }}
    .stat-box {{ background: #1b1c20; border: 1px solid #292b32; border-radius: 8px; padding: 14px; text-align: center; }}
    .stat-val {{ font-size: 22px; font-weight: 800; color: #ffffff; margin-bottom: 4px; }}
    .stat-lbl {{ font-size: 11px; color: #888c96; text-transform: uppercase; letter-spacing: 0.05em; }}
    .device-row {{ display: flex; justify-content: space-between; background: #1b1c20; border: 1px solid #292b32; border-radius: 6px; padding: 12px 16px; margin: 16px 0; font-size: 13px; color: #c0c3cc; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 13px; }}
    th {{ text-align: left; padding: 6px 12px; color: #888c96; font-size: 11px; text-transform: uppercase; border-bottom: 1px solid #292b32; }}
    .footer {{ font-size: 12px; color: #888c96; margin-top: 24px; border-top: 1px solid #292b32; padding-top: 16px; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="badge">Analytics Report (IST)</div>
    <h2>Daily Visitor Summary (IST)</h2>
    <p style="color: #888c96; font-size: 13px; margin: 0 0 16px;">Reporting Window (IST): {summary['current_start']} &mdash; {summary['current_end']}</p>

    <div class="grid">
      <div class="stat-box">
        <div class="stat-val">{tot}</div>
        <div class="stat-lbl">Visits ({trend})</div>
      </div>
      <div class="stat-box">
        <div class="stat-val">{uniq}</div>
        <div class="stat-lbl">Unique Visitors</div>
      </div>
      <div class="stat-box">
        <div class="stat-val">{sess}</div>
        <div class="stat-lbl">Sessions</div>
      </div>
    </div>

    <div class="device-row">
      <span>Desktop: <strong style="color: #fff;">{dev['desktop']}</strong></span>
      <span>Mobile: <strong style="color: #fff;">{dev['mobile']}</strong></span>
      <span>Tablet: <strong style="color: #fff;">{dev['tablet']}</strong></span>
    </div>

    <h3 style="font-size: 14px; color: #fff; margin-top: 24px; margin-bottom: 8px;">Top Visited Paths</h3>
    <table>
      <thead>
        <tr><th>Page Path</th><th style="text-align: right;">Views</th></tr>
      </thead>
      <tbody>
        {pages_html}
      </tbody>
    </table>

    <div class="footer">
      Privacy-first analytics summary automatically dispatched by your personal portfolio backend.
    </div>
  </div>
</body>
</html>"""

    return subject, text_body, html_body

def send_daily_summary(db: Session, hours: int = 24, to_email: str = None) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Computes summary data and dispatches the email report.
    Returns (success: bool, status_message: str, summary_data: dict).
    """
    data = generate_visitor_summary_data(db, hours=hours)
    subject, text_body, html_body = format_visitor_summary_email(data)
    ok, msg = send_email_smtp(subject, text_body, html_body, to_email=to_email)
    return ok, msg, data

if __name__ == "__main__":
    from .database import SessionLocal
    with SessionLocal() as db:
        ok, msg, data = send_daily_summary(db, hours=24)
        print(f"Summary dispatched: {ok} ({msg})")
        print(f"Total visits in last 24h: {data['total_visits']}, Unique: {data['unique_visitors']}")
