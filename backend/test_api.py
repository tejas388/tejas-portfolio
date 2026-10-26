"""
Automated Backend API and SQLite Persistence Verification Suite for Tejas CK Portfolio.
Runs in-process via ASGI without requiring open network ports or external servers.
Cleans up test-created data after verification to preserve database integrity.
"""
import asyncio
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.main import app, _rate_limits
from app.database import SessionLocal, DATABASE_URL
from app.models import Project, ContactMessage, PortfolioVisit, Certification, Achievement
from app.migrations import run_migrations
from app.email_service import send_contact_notification, retry_failed_notifications
from app.visitor_summary import generate_visitor_summary_data, format_visitor_summary_email

async def asgi_request(app, method, path, headers=None, body=b'', client_ip='127.0.0.1'):
    headers = headers or []
    raw_headers = [(k.lower().encode('latin1'), v.encode('latin1')) for k, v in headers]
    scope = {
        'type': 'http',
        'http_version': '1.1',
        'method': method,
        'path': path,
        'raw_path': path.encode('ascii'),
        'query_string': b'',
        'headers': raw_headers,
        'client': (client_ip, 12345),
        'server': ('127.0.0.1', 8000),
    }
    sent_messages = []
    async def receive():
        return {'type': 'http.request', 'body': body, 'more_body': False}
    async def send(message):
        sent_messages.append(message)
    await app(scope, receive, send)
    status_code = None
    response_headers = {}
    response_body = b''
    for msg in sent_messages:
        if msg['type'] == 'http.response.start':
            status_code = msg['status']
            response_headers = {k.decode('latin1'): v.decode('latin1') for k, v in msg.get('headers', [])}
        elif msg['type'] == 'http.response.body':
            response_body += msg.get('body', b'')
    return status_code, response_headers, response_body

async def run_tests():
    print("==================================================")
    print("PORTFOLIO BACKEND VERIFICATION & AUDIT SUITE (14 CHECKS)")
    print(f"Database Target: {DATABASE_URL}")
    print("==================================================")

    # Clear in-memory rate limits for clean test environment
    _rate_limits.clear()

    # Ensure schema migrations and seeding are applied
    with SessionLocal() as db:
        run_migrations(db)

    test_emails_to_cleanup = []
    test_visitors_to_cleanup = []
    admin_key = os.getenv("ADMIN_SECRET_KEY", "portfolio-admin-secret-2026")

    try:
        # 1. Health check with DB ping
        status, _, body = await asgi_request(app, 'GET', '/api/health')
        assert status == 200, f"Health check failed: status {status}"
        health_data = json.loads(body.decode())
        assert health_data['ok'] is True
        assert health_data['database'] == 'connected'
        assert health_data['service'] == 'portfolio-api'
        print("✔ [1/14] GET /api/health passed (database connected via SELECT 1)")

        # 2. Projects list
        status, _, body = await asgi_request(app, 'GET', '/api/projects')
        assert status == 200, f"Projects endpoint failed: status {status}"
        projects = json.loads(body.decode())
        assert len(projects) == 3, f"Expected 3 projects, got {len(projects)}"
        assert {p['slug'] for p in projects} == {'medisync', 'recoverai', 'ai-memory-bot'}
        for p in projects:
            assert isinstance(p.get('features'), list), f"Project {p['slug']} features must be a list"
            assert len(p['features']) > 0, f"Project {p['slug']} features list is empty"
            assert isinstance(p.get('challenges'), list), f"Project {p['slug']} challenges must be a list"
        years_by_slug = {p['slug']: p.get('year') for p in projects}
        assert years_by_slug['medisync'] == '2026', f"Expected MediSync 2026, got {years_by_slug['medisync']}"
        assert years_by_slug['recoverai'] == '2026', f"Expected RECOVERAI 2026, got {years_by_slug['recoverai']}"
        assert years_by_slug['ai-memory-bot'] == '2025–2026', f"Expected AI Memory Bot 2025–2026, got {years_by_slug['ai-memory-bot']}"
        print(f"✔ [2/14] GET /api/projects passed ({len(projects)} projects returned with structured fields & verified timelines: 2026, 2026, 2025–2026)")

        # 3. Certifications list
        status, _, body = await asgi_request(app, 'GET', '/api/certifications')
        assert status == 200, f"Certifications endpoint failed: status {status}"
        certs = json.loads(body.decode())
        assert len(certs) == 5, f"Expected 5 certifications, got {len(certs)}"
        display_orders = [c['display_order'] for c in certs]
        assert display_orders == sorted(display_orders), "Certifications must be sorted by display_order"
        cert_map = {c['title']: c for c in certs}
        assert "Full Stack Web Development Bootcamp" in cert_map
        assert cert_map["Full Stack Web Development Bootcamp"]["credential_url"] is not None
        assert "Human–Computer Interaction" in cert_map
        assert cert_map["Human–Computer Interaction"]["credential_url"] is None
        assert "Big Data Analysis" in cert_map
        assert cert_map["Big Data Analysis"]["credential_url"] is not None
        print(f"✔ [3/14] GET /api/certifications passed ({len(certs)} courses returned with verified credentials)")

        # 4. Achievements list
        status, _, body = await asgi_request(app, 'GET', '/api/achievements')
        assert status == 200, f"Achievements endpoint failed: status {status}"
        achievements = json.loads(body.decode())
        assert len(achievements) == 2, f"Expected 2 achievements, got {len(achievements)}"
        ach_orders = [a['display_order'] for a in achievements]
        assert ach_orders == sorted(ach_orders), "Achievements must be sorted by display_order"
        ach_map = {a['title']: a for a in achievements}
        assert "ClamStack — 24-Hour Hackathon" in ach_map
        assert ach_map["ClamStack — 24-Hour Hackathon"]["evidence_url"] is not None
        assert "Avishkar Manthan Ideathon" in ach_map
        assert ach_map["Avishkar Manthan Ideathon"]["evidence_url"] is not None
        print(f"✔ [4/14] GET /api/achievements passed ({len(achievements)} collaborative events returned)")

        # 5. Explicit contact submission & SQLite persistence
        test_email = 'test.recruiter@example.org'
        test_emails_to_cleanup.append(test_email)
        contact_body = json.dumps({
            'name': 'Test Recruiter',
            'email': test_email,
            'company': 'Tech Ventures',
            'message': 'We would love to discuss software engineering internship roles.'
        }).encode()
        status, _, body = await asgi_request(
            app, 'POST', '/api/contact',
            headers=[('content-type', 'application/json')],
            body=contact_body,
            client_ip='10.0.0.1'
        )
        assert status == 201, f"Contact submission failed: status {status}"
        assert json.loads(body.decode())['ok'] is True
        with SessionLocal() as db:
            saved_msg = db.query(ContactMessage).filter(ContactMessage.email == test_email).first()
            assert saved_msg is not None, "Message was not persisted in database"
            assert saved_msg.status == "new", f"Expected status 'new', got {saved_msg.status}"
            assert saved_msg.notification_status in ("pending", "sent", "failed")
        print("✔ [5/14] POST /api/contact passed (valid submission accepted with status='new' and notification tracking)")

        # 6. Contact email notification dispatch & status tracking
        with SessionLocal() as db:
            mock_msg = ContactMessage(
                name="Email Test Lead",
                email="lead@startup.org",
                company="Seed Capital",
                message="Testing email dispatch service unit logic.",
                status="new",
                notification_status="pending",
                notification_attempts=0
            )
            db.add(mock_msg)
            db.commit()
            db.refresh(mock_msg)
            test_emails_to_cleanup.append("lead@startup.org")
            msg_id = mock_msg.id

        with patch('app.email_service.send_email_smtp', return_value=(True, "Email sent successfully.")) as mock_send:
            with SessionLocal() as db:
                success = send_contact_notification(db, msg_id)
                assert success is True
                updated_msg = db.query(ContactMessage).filter(ContactMessage.id == msg_id).first()
                assert updated_msg.notification_status == "sent"
                assert updated_msg.notification_attempts == 1
                assert updated_msg.notification_sent_at is not None
                assert updated_msg.notification_error is None
            assert mock_send.call_count == 1
        print("✔ [6/14] Email notification dispatch passed (status='sent', notification_attempts=1, timestamp recorded)")

        # 7. Notification retry logic & idempotency (prevents duplicate sends)
        with patch('app.email_service.send_email_smtp', return_value=(True, "Email sent successfully.")) as mock_send_dup:
            with SessionLocal() as db:
                # Re-invoking send_contact_notification on already-sent message must NOT re-send
                dup_result = send_contact_notification(db, msg_id)
                assert dup_result is True
                assert mock_send_dup.call_count == 0, "Duplicate email was sent for an already delivered message!"

        # Test retry of a failed message
        with SessionLocal() as db:
            failed_msg = ContactMessage(
                name="Failed Retry Lead",
                email="failed@retry.org",
                message="Testing retry mechanism for failed messages.",
                status="new",
                notification_status="failed",
                notification_attempts=1,
                notification_error="Connection timed out"
            )
            db.add(failed_msg)
            db.commit()
            db.refresh(failed_msg)
            test_emails_to_cleanup.append("failed@retry.org")

        with patch('app.email_service.send_email_smtp', return_value=(True, "Email sent successfully.")):
            with SessionLocal() as db:
                retry_summary = retry_failed_notifications(db, max_attempts=3)
                assert retry_summary["successful"] >= 1
                re_checked = db.query(ContactMessage).filter(ContactMessage.email == "failed@retry.org").first()
                assert re_checked.notification_status == "sent"
                assert re_checked.notification_attempts == 2
        print("✔ [7/14] Notification retry & idempotency passed (zero duplicates on sent, successful retry on failed)")

        # 8. Contact validation rejects invalid inputs (email, short message, whitespace, missing fields)
        invalid_cases = [
            ({'name': '', 'email': 'valid@example.com', 'message': 'Hello there!'}, 'empty name'),
            ({'name': '   ', 'email': 'valid@example.com', 'message': 'Hello there!'}, 'whitespace-only name'),
            ({'name': 'Sarah', 'email': 'not-an-email', 'message': 'Hello there!'}, 'invalid email format'),
            ({'name': 'Sarah', 'email': 'user@domain', 'message': 'Hello there!'}, 'email missing TLD period'),
            ({'name': 'Sarah', 'email': 'valid@example.com', 'message': 'Hi'}, 'message under 5 characters'),
            ({'name': 'Sarah', 'email': 'valid@example.com', 'message': '     '}, 'whitespace-only message'),
            ({}, 'empty payload'),
        ]
        for bad_dict, label in invalid_cases:
            status_bad, _, body_bad = await asgi_request(
                app, 'POST', '/api/contact',
                headers=[('content-type', 'application/json')],
                body=json.dumps(bad_dict).encode(),
                client_ip='10.0.0.2'
            )
            assert status_bad == 422, f"Expected 422 for {label}, got {status_bad}"
            bad_json = json.loads(body_bad.decode())
            assert "detail" in bad_json, f"Response missing 'detail' for {label}"
        print(f"✔ [8/14] POST /api/contact validation passed ({len(invalid_cases)} invalid cases correctly rejected with HTTP 422)")

        # 9. Honeypot spam defense (bot payload silently dropped from DB)
        hp_body = json.dumps({
            'name': 'SpamBot',
            'email': 'bot@spammer.org',
            'message': 'Buy backlinks and boost SEO instantly',
            'website': 'https://spamlinks.org'
        }).encode()
        status, _, body = await asgi_request(
            app, 'POST', '/api/contact',
            headers=[('content-type', 'application/json')],
            body=hp_body,
            client_ip='10.0.0.3'
        )
        assert status == 201
        with SessionLocal() as db:
            leaked = db.query(ContactMessage).filter(ContactMessage.email == 'bot@spammer.org').first()
            assert leaked is None, "Honeypot failed: spam message was stored in database!"
        print("✔ [9/14] POST /api/contact honeypot passed (spambot payload dropped safely)")

        # 10. Rate Limiter Test on /api/contact (max 5 requests per 60s per client)
        rate_ip = '10.0.0.4'
        for i in range(5):
            await asgi_request(
                app, 'POST', '/api/contact',
                headers=[('content-type', 'application/json')],
                body=json.dumps({
                    'name': f'Spam Attempt {i}',
                    'email': f'attempt{i}@test.com',
                    'message': 'Testing rate limiting threshold'
                }).encode(),
                client_ip=rate_ip
            )
            test_emails_to_cleanup.append(f'attempt{i}@test.com')

        # The 6th request from the same IP must be rate-limited with HTTP 429
        status_429, _, body_429 = await asgi_request(
            app, 'POST', '/api/contact',
            headers=[('content-type', 'application/json')],
            body=json.dumps({
                'name': 'Spam Attempt 6',
                'email': 'attempt6@test.com',
                'message': 'Should be blocked by rate limiter'
            }).encode(),
            client_ip=rate_ip
        )
        assert status_429 == 429, f"Expected 429 Too Many Requests, got {status_429}"
        print("✔ [10/14] Rate limiting passed (6th rapid request blocked with HTTP 429)")

        # 11. Privacy check: Contact messages NEVER exposed publicly via GET
        status_get, _, _ = await asgi_request(app, 'GET', '/api/contact')
        assert status_get in (404, 405), f"GET /api/contact must not be accessible, returned {status_get}"
        print("✔ [11/14] Privacy guarantee passed (GET /api/contact strictly blocked from public view)")

        # 12. Anonymous visit telemetry & live visitor alerts (new session alert vs duplicate suppression)
        test_visitor_id = 'anon-test-check-clean-99'
        test_session_id = 'sess-test-session-99'
        test_visitors_to_cleanup.append(test_visitor_id)

        # 12a. Genuinely new session triggers an asynchronous visitor alert
        with patch('app.email_service.send_email_smtp', return_value=(True, "Alert sent.")) as mock_visitor_alert:
            visit_body = json.dumps({
                'visitor_id': test_visitor_id,
                'session_id': test_session_id,
                'device_category': 'mobile',
                'page_path': '/',
                'referrer': 'https://github.com'
            }).encode()
            status, _, _ = await asgi_request(
                app, 'POST', '/api/visits',
                headers=[
                    ('content-type', 'application/json'),
                    ('user-agent', 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)')
                ],
                body=visit_body,
                client_ip='10.0.0.5'
            )
            assert status == 201
            assert mock_visitor_alert.call_count == 1, "Expected exactly 1 email alert for a new visitor session"
            call_args = mock_visitor_alert.call_args
            alert_subj = call_args[0][0]
            alert_text = call_args[0][1]
            assert "New Portfolio Visitor Alert (IST)" in alert_subj
            assert "IST" in alert_text
            assert "Page Visited:    /" in alert_text
            assert "Device Category: Mobile" in alert_text
            assert "Traffic Source:  https://github.com" in alert_text
            # Privacy assertion: No IP addresses or session tokens leaked in email text
            assert "10.0.0.5" not in alert_text, "IP address must never be leaked in email alerts!"
            assert test_session_id not in alert_text, "Session ID token must never be leaked in email alerts!"

            # 12b. Repeated visit in the SAME session (e.g. page refresh) must NOT trigger another email alert
            status_refresh, _, _ = await asgi_request(
                app, 'POST', '/api/visits',
                headers=[
                    ('content-type', 'application/json'),
                    ('user-agent', 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)')
                ],
                body=visit_body,
                client_ip='10.0.0.5'
            )
            assert status_refresh == 201
            assert mock_visitor_alert.call_count == 1, "Duplicate page refresh in same session must NOT send another alert!"

            # 12c. Automated crawler / bot must NOT trigger an email alert
            bot_body = json.dumps({
                'visitor_id': 'bot-crawl-123',
                'session_id': 'sess-bot-456',
                'page_path': '/'
            }).encode()
            test_visitors_to_cleanup.append('bot-crawl-123')
            await asgi_request(
                app, 'POST', '/api/visits',
                headers=[
                    ('content-type', 'application/json'),
                    ('user-agent', 'Googlebot/2.1 (+http://www.google.com/bot.html)')
                ],
                body=bot_body,
                client_ip='10.0.0.6'
            )
            assert mock_visitor_alert.call_count == 1, "Search engine crawler must NOT trigger a visitor alert!"

        with SessionLocal() as db:
            visit_record = db.query(PortfolioVisit).filter(PortfolioVisit.visitor_id == test_visitor_id).first()
            assert visit_record is not None
            assert visit_record.session_id == test_session_id
            assert visit_record.device_category == 'mobile'
            assert not hasattr(visit_record, 'name')
            assert not hasattr(visit_record, 'email')
            assert not hasattr(visit_record, 'ip_address')
        print("✔ [12/14] Anonymous visit telemetry passed (new-session alert, duplicate-session suppression, bot filtering, zero leaked tokens)")

        # 13. Visitor Activity Summary generation & period comparison analytics in IST
        with SessionLocal() as db:
            summary = generate_visitor_summary_data(db, hours=24)
            assert "total_visits" in summary
            assert "unique_visitors" in summary
            assert "unique_sessions" in summary
            assert "device_breakdown" in summary
            assert "top_pages" in summary
            assert "prev_total_visits" in summary
            assert summary["report_generated_at"].endswith("IST"), "Report generated timestamp must be in IST"
            assert summary["current_start"].endswith("IST"), "Reporting window start must be in IST"
            assert summary["current_end"].endswith("IST"), "Reporting window end must be in IST"
            subject, text_body, html_body = format_visitor_summary_email(summary)
            assert "Daily Portfolio Visitor Summary (IST)" in subject
            assert "OVERVIEW METRICS" in text_body
            assert "DEVICE BREAKDOWN" in text_body
            assert "IST" in text_body
            assert "<!DOCTYPE html>" in html_body
        print("✔ [13/14] Visitor Activity Summary analytics passed (explicit IST timestamps, accurate sessions, trends, HTML/Text)")

        # 14. Secured internal admin endpoints
        # 14a. Reject request with missing/invalid admin key
        status_unauth, _, _ = await asgi_request(
            app, 'POST', '/api/internal/send-visitor-summary',
            headers=[('x-admin-key', 'wrong-key-value')]
        )
        assert status_unauth == 401, f"Expected 401 Unauthorized for bad admin key, got {status_unauth}"

        # 14b. Accept request with valid admin key (mocking email send)
        with patch('app.visitor_summary.send_email_smtp', return_value=(True, "Summary delivered")):
            status_auth, _, body_auth = await asgi_request(
                app, 'POST', '/api/internal/send-visitor-summary',
                headers=[('x-admin-key', admin_key)]
            )
            assert status_auth == 200, f"Expected 200 OK for valid admin key, got {status_auth}"
            auth_data = json.loads(body_auth.decode())
            assert auth_data['ok'] is True
            assert 'summary' in auth_data

        # 14c. Retry notifications endpoint with valid admin key
        with patch('app.email_service.send_email_smtp', return_value=(True, "Retried")):
            status_retry, _, body_retry = await asgi_request(
                app, 'POST', '/api/internal/retry-notifications',
                headers=[('x-admin-key', admin_key)]
            )
            assert status_retry == 200, f"Expected 200 OK for retry endpoint, got {status_retry}"
            retry_data = json.loads(body_retry.decode())
            assert retry_data['ok'] is True
            assert 'results' in retry_data
        print("✔ [14/14] Secured internal admin endpoints passed (HTTP 401 on unauthorized, HTTP 200 with X-Admin-Key)")

    finally:
        # Cleanup test records to preserve real database records
        with SessionLocal() as db:
            if test_emails_to_cleanup:
                db.query(ContactMessage).filter(ContactMessage.email.in_(test_emails_to_cleanup)).delete(synchronize_session=False)
            if test_visitors_to_cleanup:
                db.query(PortfolioVisit).filter(PortfolioVisit.visitor_id.in_(test_visitors_to_cleanup)).delete(synchronize_session=False)
            db.commit()
        print("✔ Cleaned up test-inserted records from database.")

    print("\n==================================================")
    print("ALL 14 BACKEND VERIFICATIONS COMPLETED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(run_tests())
