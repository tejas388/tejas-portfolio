"""
Email notification service for Tejas CK Portfolio.
Supports Gmail SMTP with STARTTLS and App Password authentication.
Includes defensive error handling, timeout protection, retry management,
and simulated mode when SMTP credentials are not yet configured.
"""
import logging
import os
import smtplib
import ssl
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from email.message import EmailMessage
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from .models import ContactMessage

IST_TZ = ZoneInfo("Asia/Kolkata")

try:
    import certifi
    CA_FILE = certifi.where()
except ImportError:
    CA_FILE = None

logger = logging.getLogger("portfolio.email")

def create_verified_ssl_context() -> ssl.SSLContext:
    """
    Creates an SSL context with certificate and hostname verification strictly enabled.
    Supplies certifi's vetted Mozilla CA bundle to prevent SSLCertVerificationError on macOS.
    """
    if CA_FILE:
        return ssl.create_default_context(cafile=CA_FILE)
    return ssl.create_default_context()

def get_smtp_config():
    """Reads SMTP configuration from environment with secure defaults."""
    host = os.getenv("SMTP_HOST", "smtp.gmail.com").strip()
    port_str = os.getenv("SMTP_PORT", "587").strip()
    try:
        port = int(port_str)
    except ValueError:
        port = 587

    username = os.getenv("SMTP_USERNAME", "").strip()
    app_password = os.getenv("SMTP_APP_PASSWORD", "").strip()
    from_email = os.getenv("NOTIFICATION_FROM_EMAIL", "").strip() or username or "noreply@portfolio.local"
    to_email = os.getenv("NOTIFICATION_TO_EMAIL", "").strip() or username or "tejas2005patel@gmail.com"
    use_tls = os.getenv("SMTP_USE_TLS", "true").lower() in ("true", "1", "yes")
    
    timeout_str = os.getenv("SMTP_TIMEOUT", "10").strip()
    try:
        timeout = int(timeout_str)
    except ValueError:
        timeout = 10

    return {
        "host": host,
        "port": port,
        "username": username,
        "app_password": app_password,
        "from_email": from_email,
        "to_email": to_email,
        "use_tls": use_tls,
        "timeout": timeout,
    }

def is_smtp_configured() -> bool:
    """Checks whether SMTP credentials are fully provided."""
    config = get_smtp_config()
    return bool(config["username"] and config["app_password"])

def send_email_smtp(
    subject: str,
    text_body: str,
    html_body: Optional[str] = None,
    to_email: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Sends an email via Gmail SMTP using STARTTLS.
    Never exposes passwords in logs or exceptions.
    Returns (success: bool, status_message: str).
    """
    config = get_smtp_config()
    target_to = to_email or config["to_email"]

    if not config["username"] or not config["app_password"]:
        logger.info(
            "SMTP credentials not configured (simulation mode). Email not dispatched: '%s' -> %s",
            subject,
            target_to
        )
        return True, "Simulation mode: SMTP credentials not set. Message recorded locally."

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = config["from_email"]
    msg["To"] = target_to
    msg.set_content(text_body)

    if html_body:
        msg.add_alternative(html_body, subtype="html")

    server = None
    try:
        if config["port"] == 465:
            # SSL
            context = create_verified_ssl_context()
            server = smtplib.SMTP_SSL(config["host"], config["port"], timeout=config["timeout"], context=context)
        else:
            # STARTTLS
            server = smtplib.SMTP(config["host"], config["port"], timeout=config["timeout"])
            server.ehlo()
            if config["use_tls"]:
                context = create_verified_ssl_context()
                server.starttls(context=context)
                server.ehlo()

        server.login(config["username"], config["app_password"])
        server.send_message(msg)
        logger.info("Email notification delivered successfully to %s: '%s'", target_to, subject)
        return True, "Email sent successfully."

    except smtplib.SMTPAuthenticationError:
        err = "Authentication failed. Please verify your Gmail App Password."
        logger.error("SMTP Authentication Error when sending to %s", target_to)
        return False, err
    except (smtplib.SMTPException, TimeoutError, OSError) as exc:
        err = f"SMTP transmission error: {type(exc).__name__}"
        logger.error("SMTP error sending email to %s: %s", target_to, type(exc).__name__)
        return False, err
    except Exception as exc:
        err = f"Unexpected email error: {type(exc).__name__}"
        logger.error("Unexpected error in email dispatch: %s", type(exc).__name__)
        return False, err
    finally:
        if server:
            try:
                server.quit()
            except Exception:
                pass

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
