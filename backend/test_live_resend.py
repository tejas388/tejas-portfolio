"""
Controlled live test for Resend email delivery.
Reads local configuration from backend/.env via email_service.
NEVER prints or exposes API keys or secrets.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add backend directory to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Ensure environment is loaded from backend/.env
load_dotenv(BASE_DIR / ".env")

from app.email_service import is_smtp_configured, send_email_smtp, get_smtp_config

def main():
    if not is_smtp_configured():
        print("[BLOCKER] Resend is not fully configured in backend/.env.")
        cfg = get_smtp_config()
        print(f"  - RESEND_API_KEY present: {bool(cfg['api_key'])}")
        print(f"  - NOTIFICATION_FROM_EMAIL present: {bool(cfg['from_email'])}")
        print(f"  - NOTIFICATION_TO_EMAIL present: {bool(cfg['to_email'])}")
        sys.exit(1)

    cfg = get_smtp_config()
    print("Configuration verified (presence checked without logging secrets).")
    print(f"Target Recipient: {cfg['to_email']}")
    print(f"Sender: {cfg['from_email']}")
    print("Initiating controlled test send via Resend HTTPS API...")

    subject = "Portfolio Resend Integration Live Verification (IST)"
    text_body = """Hello Tejas,

This is a controlled end-to-end verification test from your portfolio backend.
The Resend HTTPS API integration has been successfully updated with verified TLS certificates.

Configuration Highlights:
- Provider: Resend HTTPS API
- Verified CA Bundle: certifi
- Timezone: Indian Standard Time (IST)
- Service: Tejas CK Portfolio Backend

Note: This verifies that the Resend API accepted the request for delivery.
"""

    html_body = """<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: sans-serif; background: #0f1012; color: #f5f5f7; padding: 24px;">
  <div style="max-width: 560px; margin: 0 auto; background: #151619; border: 1px solid #292b32; border-radius: 8px; padding: 24px;">
    <h2 style="color: #ff454b; margin-top: 0;">Portfolio Live Verification (IST)</h2>
    <p>Your portfolio backend has successfully connected to the Resend HTTPS API using verified TLS certificates.</p>
    <div style="background: #1b1c20; border: 1px solid #292b32; border-radius: 6px; padding: 14px; margin: 16px 0; font-size: 13px; color: #c0c3cc;">
      <p style="margin: 4px 0;"><strong>Status:</strong> Request Accepted by Resend API</p>
      <p style="margin: 4px 0;"><strong>Recipient:</strong> tejas2005patel@gmail.com</p>
      <p style="margin: 4px 0;"><strong>CA Bundle:</strong> Verified certifi root certificates</p>
    </div>
    <p style="font-size: 12px; color: #888c96;">Automated one-time test dispatched from local developer environment.</p>
  </div>
</body>
</html>"""

    ok, msg = send_email_smtp(subject, text_body, html_body)

    if ok:
        print("\n[SUCCESS] " + msg)
        print("Resend has officially accepted the email for delivery.")
        print("Please check your Gmail inbox (and Spam/Updates folder) at tejas2005patel@gmail.com to confirm final delivery.")
    else:
        print("\n[FAILED] " + msg)

if __name__ == "__main__":
    main()
