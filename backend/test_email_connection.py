"""
Safe local Gmail SMTP verification script for Tejas CK Portfolio.
Attempts to establish an authenticated TLS connection and dispatch a single test email
WITHOUT exposing passwords, secrets, or credential strings in terminal output or logs.
"""
import os
import sys
import smtplib
import ssl
from pathlib import Path
from email.message import EmailMessage
from datetime import datetime, timezone

# Load backend directory and environment safely
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

try:
    from dotenv import load_dotenv
    # Load backend/.env if present
    env_path = backend_dir / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    else:
        load_dotenv()
except ImportError:
    pass

try:
    import certifi
    CA_FILE = certifi.where()
except ImportError:
    CA_FILE = None

def get_ssl_context() -> ssl.SSLContext:
    if CA_FILE:
        return ssl.create_default_context(cafile=CA_FILE)
    return ssl.create_default_context()

def mask_email(email_str: str) -> str:
    if not email_str or "@" not in email_str:
        return "[NOT SET]"
    parts = email_str.split("@")
    user = parts[0]
    domain = parts[1]
    masked_user = user[:2] + "***" + user[-1:] if len(user) > 3 else user[0] + "***"
    return f"{masked_user}@{domain}"

def run_smtp_verification():
    print("=" * 60)
    print("GMAIL SMTP SAFE VERIFICATION TEST")
    print("=" * 60)

    host = os.getenv("SMTP_HOST", "smtp.gmail.com").strip()
    port_str = os.getenv("SMTP_PORT", "587").strip()
    try:
        port = int(port_str)
    except ValueError:
        port = 587

    username = os.getenv("SMTP_USERNAME", "").strip()
    app_password = os.getenv("SMTP_APP_PASSWORD", "").strip()
    from_email = os.getenv("NOTIFICATION_FROM_EMAIL", "").strip() or username
    to_email = os.getenv("NOTIFICATION_TO_EMAIL", "").strip() or username

    print(f"Target SMTP Host:    {host}:{port}")
    print(f"Sender Account:      {mask_email(username)}")
    print(f"Destination Inbox:   {mask_email(to_email)}")
    
    if not app_password:
        print("Password Status:     [NOT CONFIGURED]")
        print("\n❌ Error: SMTP_APP_PASSWORD is not set.")
        print("Please configure your 16-character Google App Password in backend/.env.")
        print("See backend/.env.example for instructions.")
        sys.exit(1)
    else:
        print(f"Password Status:     [CONFIGURED - {len(app_password)} characters, value hidden]")

    print("-" * 60)
    print("Attempting TLS handshake and authentication...")

    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    msg = EmailMessage()
    msg["Subject"] = f"Portfolio SMTP Diagnostic Test [{now_utc}]"
    msg["From"] = from_email
    msg["To"] = to_email
    msg.set_content(
        f"This is an automated diagnostic test email sent from your portfolio backend.\n\n"
        f"Host:       {host}:{port}\n"
        f"Timestamp:  {now_utc}\n"
        f"Status:     SMTP connection, TLS handshake, and authentication succeeded.\n\n"
        f"Your Gmail SMTP setup is working correctly for contact inquiries and daily summaries."
    )

    server = None
    try:
        if port == 465:
            ctx = get_ssl_context()
            server = smtplib.SMTP_SSL(host, port, timeout=12, context=ctx)
        else:
            server = smtplib.SMTP(host, port, timeout=12)
            server.ehlo()
            ctx = get_ssl_context()
            server.starttls(context=ctx)
            server.ehlo()

        server.login(username, app_password)
        server.send_message(msg)

        print("\n✔ [SMTP ACCEPTED] Message accepted by Google SMTP server for delivery!")
        print(f"✔ Target: {mask_email(to_email)}")
        print("\nNEXT STEP TO VERIFY ACTUAL DELIVERY:")
        print("1. Open your Gmail inbox for the recipient account.")
        print("2. Look for the email with subject: 'Portfolio SMTP Diagnostic Test'.")
        print("3. Check Spam or Promotions folder if it does not appear in your primary inbox within 1 minute.")
        print("=" * 60)

    except smtplib.SMTPAuthenticationError:
        print("\n❌ Authentication Failed (SMTPAuthenticationError):")
        print("- Verify that 2-Step Verification is turned ON for your Google Account.")
        print("- Verify that you generated an 'App Password' (16 lowercase letters), NOT your standard account password.")
        print("- Ensure there are no extra spaces or quotation marks in the SMTP_APP_PASSWORD variable.")
        sys.exit(1)
    except smtplib.SMTPConnectError as e:
        print(f"\n❌ Connection Error: Unable to connect to {host}:{port}. Check your network or firewall.")
        sys.exit(1)
    except (TimeoutError, smtplib.SMTPException, OSError) as e:
        print(f"\n❌ Transmission Error ({type(e).__name__}): {e}")
        print("Note: If running inside a restricted terminal sandbox, external network access may be blocked.")
        print("Run this command directly in your macOS terminal outside any sandbox.")
        sys.exit(1)
    finally:
        if server:
            try:
                server.quit()
            except Exception:
                pass

if __name__ == "__main__":
    run_smtp_verification()
