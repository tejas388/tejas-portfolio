"""Email notifications for the portfolio, delivered using Resend's HTTPS API."""

import json
import logging
import os
import socket
import ssl
from datetime import datetime, timezone
from typing import Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session
from .models import ContactMessage

try:
    import certifi
    _CA_FILE = certifi.where()
except ImportError:
    _CA_FILE = None

IST_TZ = ZoneInfo("Asia/Kolkata")
logger = logging.getLogger("portfolio.email")


def _get_ssl_context() -> ssl.SSLContext:
    """Creates a strictly verified SSL context with a trusted CA bundle."""
    if _CA_FILE:
        context = ssl.create_default_context(cafile=_CA_FILE)
    else:
        context = ssl.create_default_context()
    context.check_hostname = True
    context.verify_mode = ssl.CERT_REQUIRED
    return context


def get_smtp_config():
    """Legacy-compatible configuration helper; delivery now uses Resend."""
    return {
        "api_key": os.getenv("RESEND_API_KEY", "").strip(),
        "from_email": os.getenv("NOTIFICATION_FROM_EMAIL", "").strip(),
        "to_email": os.getenv(
            "NOTIFICATION_TO_EMAIL", "tejas2005patel@gmail.com"
        ).strip(),
        "timeout": 15,
    }


def is_smtp_configured() -> bool:
    """Keep the legacy function name so existing imports continue to work."""
    config = get_smtp_config()
    return bool(
        config["api_key"] and config["from_email"] and config["to_email"]
    )


def send_email_smtp(
    subject: str,
    text_body: str,
    html_body: Optional[str] = None,
    to_email: Optional[str] = None,
) -> Tuple[bool, str]:
    """
    Send an email through Resend HTTPS API.
    Returns (success: bool, status_message: str).
    Guarantees strict TLS certificate verification and safe diagnostic logging.
    """
    config = get_smtp_config()
    target_to = to_email or config["to_email"]

    if not config["api_key"]:
        logger.error("Email not sent: RESEND_API_KEY is not configured.")
        return False, "Email delivery is not configured: missing RESEND_API_KEY."
    if not config["from_email"] or not target_to:
        logger.error("Email not sent: sender (%s) or recipient (%s) is missing.", bool(config["from_email"]), bool(target_to))
        return False, "Email sender or recipient is not configured."

    payload = {
        "from": config["from_email"],
        "to": [target_to],
        "subject": subject,
        "text": text_body,
    }
    if html_body:
        payload["html"] = html_body

    request = Request(
        "https://api.resend.com/emails",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json",
            "User-Agent": "Tejas-Portfolio/1.0",
        },
        method="POST",
    )

    try:
        ssl_ctx = _get_ssl_context()
        with urlopen(request, timeout=config["timeout"], context=ssl_ctx) as response:
            response_body = response.read().decode("utf-8", errors="replace")
            if response.status not in (200, 201):
                logger.error("Resend API returned unexpected HTTP status %s.", response.status)
                return False, f"Email provider returned HTTP {response.status}."

        try:
            result = json.loads(response_body)
        except json.JSONDecodeError:
            result = {}

        email_id = result.get("id")
        logger.info("Email accepted by Resend (id: %s) for recipient %s.", email_id or 'unknown', target_to)
        return True, f"Email accepted by Resend for processing (id: {email_id or 'accepted'}). Note: Acceptance indicates queued for dispatch; delivery depends on recipient server acceptance."

    except HTTPError as exc:
        # Never log Authorization header or API keys
        try:
            raw_err = exc.read().decode("utf-8", errors="replace")[:400]
            err_json = json.loads(raw_err)
            err_msg = err_json.get("message") or err_json.get("name") or raw_err
        except Exception:
            err_msg = str(exc)

        if exc.code == 401:
            category = "Authentication failed (invalid or expired RESEND_API_KEY)"
        elif exc.code in (403, 422):
            category = "Sender or recipient policy restriction (e.g. unverified domain or sandbox limitation)"
        elif exc.code == 429:
            category = "Rate limit exceeded on Resend API"
        else:
            category = f"Resend API error (HTTP {exc.code})"

        logger.error("Resend HTTP rejection [HTTP %s]: %s — detail: %s", exc.code, category, err_msg)
        return False, f"Resend rejected email (HTTP {exc.code}): {category}. {err_msg}"

    except URLError as exc:
        reason = exc.reason
        if isinstance(reason, ssl.SSLCertVerificationError):
            logger.error("Resend TLS certificate verification failed: %s", reason)
            return False, f"TLS certificate verification error: {reason}."
        if isinstance(reason, (TimeoutError, socket.timeout)) or "timed out" in str(reason).lower():
            logger.error("Resend connection timed out: %s", reason)
            return False, f"Connection timed out while reaching Resend API: {reason}."
        logger.error("Resend network connection failed (%s): %s", type(reason).__name__, reason)
        return False, f"Network connection error to Resend API ({type(reason).__name__}): {reason}."

    except TimeoutError as exc:
        logger.error("Resend request timed out after %s seconds: %s", config["timeout"], exc)
        return False, f"Resend request timed out after {config['timeout']} seconds."

    except Exception as exc:
        logger.error("Unexpected email service error: %s: %s", type(exc).__name__, exc)
        return False, f"Unexpected email error: {type(exc).__name__}."


def send_contact_notification(db: Session, message_id: int) -> bool:
    """
    Sends an email notification for a stored contact inquiry.
    Prevents duplicate emails if already sent.
    Updates ContactMessage.notification_status in the database.
    """
    contact = db.query(ContactMessage).filter(ContactMessage.id == message_id).first()
    if not contact:
        logger.warning("ContactMessage id %s not found for email notification", message_id)
        return False

    # Prevent duplicate notification
    if contact.notification_status == "sent":
        logger.info("Notification for message id %s was already sent. Skipping duplicate.", message_id)
        return True

    dt = contact.created_at or datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    formatted_date_ist = dt.astimezone(IST_TZ).strftime("%Y-%m-%d %I:%M:%S %p IST")

    subject = f"New Portfolio Contact Message from {contact.name} (IST)"

    text_body = f"""You have received a new contact inquiry through your portfolio website.

Sender Name:  {contact.name}
Email:        {contact.email}
Company:      {contact.company or 'Not specified'}
Submitted At: {formatted_date_ist}
Message ID:   #{contact.id}

Message:
------------------------------------------------------------
{contact.message}
------------------------------------------------------------

Security & Privacy Notice:
This message was submitted through your personal developer portfolio contact form.
Your email address and credentials are never exposed publicly.
"""

    company_line = f"<p style='margin: 4px 0;'><strong>Company:</strong> {contact.company}</p>" if contact.company else ""
    html_body = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: #0f1012; color: #f5f5f7; margin: 0; padding: 24px; }}
    .container {{ max-width: 600px; margin: 0 auto; background: #151619; border: 1px solid #292b32; border-radius: 10px; padding: 28px; }}
    .badge {{ display: inline-block; padding: 4px 10px; background: rgba(255, 69, 75, 0.12); color: #ff454b; font-size: 11px; font-weight: 700; letter-spacing: 0.08em; border-radius: 4px; text-transform: uppercase; margin-bottom: 12px; }}
    h2 {{ color: #ffffff; margin-top: 0; font-size: 20px; }}
    .meta-box {{ background: #1b1c20; border: 1px solid #292b32; border-radius: 6px; padding: 16px; margin: 20px 0; font-size: 14px; line-height: 1.6; color: #c0c3cc; }}
    .meta-box strong {{ color: #ffffff; }}
    .message-box {{ background: #101114; border-left: 3px solid #ff454b; padding: 18px; border-radius: 0 6px 6px 0; font-size: 15px; line-height: 1.7; color: #f5f5f7; white-space: pre-wrap; margin: 20px 0; }}
    .footer {{ font-size: 12px; color: #888c96; margin-top: 24px; border-top: 1px solid #292b32; padding-top: 16px; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="badge">Portfolio Inquiry (IST)</div>
    <h2>New Message from {contact.name}</h2>
    
    <div class="meta-box">
      <p style="margin: 4px 0;"><strong>Sender:</strong> {contact.name}</p>
      <p style="margin: 4px 0;"><strong>Email:</strong> <a href="mailto:{contact.email}" style="color: #ff454b; text-decoration: none;">{contact.email}</a></p>
      {company_line}
      <p style="margin: 4px 0;"><strong>Timestamp (IST):</strong> {formatted_date_ist}</p>
      <p style="margin: 4px 0;"><strong>Database Record:</strong> #{contact.id}</p>
    </div>

    <div class="message-box">
{contact.message}
    </div>

    <div class="footer">
      This notification was automatically generated by your personal portfolio backend API upon valid contact submission.
    </div>
  </div>
</body>
</html>"""

    success, msg = send_email_smtp(subject, text_body, html_body)

    contact.notification_attempts = (contact.notification_attempts or 0) + 1
    if success:
        contact.notification_status = "sent"
        contact.notification_sent_at = datetime.now(timezone.utc)
        contact.notification_error = None
    else:
        contact.notification_status = "failed"
        contact.notification_error = msg[:500]

    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.error("Failed to commit notification status for message %s: %s", message_id, exc)

    return success

def retry_failed_notifications(db: Session, max_attempts: int = 3) -> dict:
    """
    Retries any failed contact email notifications up to max_attempts.
    Guarantees no duplicate emails for previously sent notifications.
    """
    failed_messages = (
        db.query(ContactMessage)
        .filter(
            ContactMessage.notification_status == "failed",
            ContactMessage.notification_attempts < max_attempts
        )
        .all()
    )

    results = {"total_retried": len(failed_messages), "successful": 0, "failed": 0}
    for msg in failed_messages:
        ok = send_contact_notification(db, msg.id)
        if ok:
            results["successful"] += 1
        else:
            results["failed"] += 1

    return results

def send_visitor_alert_notification(db: Session, visit_id: int) -> Tuple[bool, str]:
    """
    Sends an immediate email notification when a genuinely new anonymous visitor session is recorded.
    Never exposes IP addresses, session tokens, personal identifiers, or secrets.
    Includes timestamp converted to IST.
    """
    from .models import PortfolioVisit
    visit = db.query(PortfolioVisit).filter(PortfolioVisit.id == visit_id).first()
    if not visit:
        logger.warning("PortfolioVisit id %s not found for visitor alert notification", visit_id)
        return False, "Visit record not found"

    # Convert timestamp to IST
    created_at = visit.created_at
    if created_at is None:
        created_at = datetime.now(timezone.utc)
    elif created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    ist_time_str = created_at.astimezone(IST_TZ).strftime("%Y-%m-%d %I:%M:%S %p IST")

    device_label = (visit.device_category or "Desktop").title()
    referrer_label = visit.referrer or "Direct / None"
    page_label = visit.page_path or "/"

    subject = f"New Portfolio Visitor Alert (IST) — {device_label}"

    text_body = f"""A new anonymous visitor session has arrived at your portfolio website.

Visit Details (IST):
------------------------------------------------------------
Timestamp:       {ist_time_str}
Page Visited:    {page_label}
Device Category: {device_label}
Traffic Source:  {referrer_label}

Privacy Note:
No IP addresses, session tokens, or personal identifiers are stored or emailed.
Only one alert is generated per unique visitor session.
"""

    html_body = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: #0f1012; color: #f5f5f7; margin: 0; padding: 24px; }}
    .container {{ max-width: 600px; margin: 0 auto; background: #151619; border: 1px solid #292b32; border-radius: 10px; padding: 28px; }}
    .badge {{ display: inline-block; padding: 4px 10px; background: rgba(255, 69, 75, 0.12); color: #ff454b; font-size: 11px; font-weight: 700; letter-spacing: 0.08em; border-radius: 4px; text-transform: uppercase; margin-bottom: 12px; }}
    h2 {{ color: #ffffff; margin-top: 0; font-size: 20px; }}
    .meta-box {{ background: #1b1c20; border: 1px solid #292b32; border-radius: 6px; padding: 16px; margin: 20px 0; font-size: 14px; line-height: 1.8; color: #c0c3cc; }}
    .meta-box strong {{ color: #ffffff; }}
    .footer {{ font-size: 12px; color: #888c96; margin-top: 24px; border-top: 1px solid #292b32; padding-top: 16px; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="badge">Live Visitor Alert (IST)</div>
    <h2>New Visitor Session Active</h2>
    
    <div class="meta-box">
      <p style="margin: 4px 0;"><strong>Time (IST):</strong> {ist_time_str}</p>
      <p style="margin: 4px 0;"><strong>Page:</strong> <code>{page_label}</code></p>
      <p style="margin: 4px 0;"><strong>Device:</strong> {device_label}</p>
      <p style="margin: 4px 0;"><strong>Referrer:</strong> {referrer_label}</p>
    </div>

    <div class="footer">
      Privacy-first anonymous telemetry alert dispatched by your personal portfolio backend.
      No IP addresses, session tokens, or personal identifiers are stored or shared.
    </div>
  </div>
</body>
</html>"""

    success, msg = send_email_smtp(subject, text_body, html_body)
    return success, msg
