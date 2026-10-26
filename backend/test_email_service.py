"""
Unit tests for the Resend email service (backend/app/email_service.py).
Mocks all HTTP requests so tests run without live network or real API keys.
Tests success, HTTP rejections (401, 403/422, 429), timeouts, SSL errors,
and missing configurations.
"""
import io
import json
import os
import socket
import ssl
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError, URLError

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.email_service import (
    get_smtp_config,
    is_smtp_configured,
    send_email_smtp,
    _get_ssl_context
)


class MockHTTPResponse:
    def __init__(self, status=200, body=b'{"id": "re_test_id_123"}'):
        self.status = status
        self._body = body

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class TestResendEmailService(unittest.TestCase):
    def setUp(self):
        self.env_patcher = patch.dict(os.environ, {
            "RESEND_API_KEY": "re_mock_test_key_xyz",
            "NOTIFICATION_FROM_EMAIL": "onboarding@resend.dev",
            "NOTIFICATION_TO_EMAIL": "tejas2005patel@gmail.com"
        })
        self.env_patcher.start()

    def tearDown(self):
        self.env_patcher.stop()

    def test_legacy_get_smtp_config(self):
        """Verifies backward compatibility of get_smtp_config dictionary structure."""
        config = get_smtp_config()
        self.assertIn("api_key", config)
        self.assertIn("from_email", config)
        self.assertIn("to_email", config)
        self.assertIn("timeout", config)
        self.assertEqual(config["api_key"], "re_mock_test_key_xyz")
        self.assertEqual(config["from_email"], "onboarding@resend.dev")
        self.assertEqual(config["to_email"], "tejas2005patel@gmail.com")

    def test_is_smtp_configured(self):
        """Verifies configuration detection when all keys are present or missing."""
        self.assertTrue(is_smtp_configured())

        with patch.dict(os.environ, {"RESEND_API_KEY": ""}):
            self.assertFalse(is_smtp_configured())

        with patch.dict(os.environ, {"NOTIFICATION_FROM_EMAIL": ""}):
            self.assertFalse(is_smtp_configured())

        with patch.dict(os.environ, {"NOTIFICATION_TO_EMAIL": ""}):
            self.assertFalse(is_smtp_configured())

    def test_missing_api_key_fails_safely(self):
        """send_email_smtp returns False immediately when API key is missing."""
        with patch.dict(os.environ, {"RESEND_API_KEY": ""}):
            with patch("app.email_service.urlopen") as mock_url:
                ok, msg = send_email_smtp("Test Subject", "Test Body")
                self.assertFalse(ok)
                self.assertIn("missing RESEND_API_KEY", msg)
                mock_url.assert_not_called()

    def test_missing_sender_or_recipient_fails_safely(self):
        """send_email_smtp returns False when sender is missing."""
        with patch.dict(os.environ, {"NOTIFICATION_FROM_EMAIL": ""}):
            with patch("app.email_service.urlopen") as mock_url:
                ok, msg = send_email_smtp("Test Subject", "Test Body")
                self.assertFalse(ok)
                self.assertIn("sender or recipient is not configured", msg)
                mock_url.assert_not_called()

    @patch("app.email_service.urlopen")
    def test_successful_resend_delivery(self, mock_urlopen):
        """Verifies Resend 200 OK parsing and acceptance message."""
        mock_urlopen.return_value = MockHTTPResponse(
            status=200,
            body=json.dumps({"id": "re_mock_accepted_456"}).encode("utf-8")
        )

        ok, msg = send_email_smtp(
            subject="Inquiry Received",
            text_body="Hello Tejas",
            html_body="<p>Hello Tejas</p>"
        )
        self.assertTrue(ok)
        self.assertIn("re_mock_accepted_456", msg)
        self.assertIn("Email accepted by Resend", msg)
        self.assertIn("Acceptance indicates queued for dispatch", msg)

        # Verify request payload
        req = mock_urlopen.call_args[0][0]
        self.assertEqual(req.full_url, "https://api.resend.com/emails")
        self.assertEqual(req.get_method(), "POST")
        self.assertIn("Bearer re_mock_test_key_xyz", req.headers["Authorization"])
        body = json.loads(req.data.decode("utf-8"))
        self.assertEqual(body["from"], "onboarding@resend.dev")
        self.assertEqual(body["to"], ["tejas2005patel@gmail.com"])
        self.assertEqual(body["subject"], "Inquiry Received")
        self.assertEqual(body["html"], "<p>Hello Tejas</p>")

    @patch("app.email_service.urlopen")
    def test_http_401_invalid_api_key(self, mock_urlopen):
        """Verifies safe error message on invalid API key (HTTP 401)."""
        err_stream = io.BytesIO(json.dumps({
            "statusCode": 401,
            "name": "authentication_error",
            "message": "API key is invalid"
        }).encode("utf-8"))
        mock_urlopen.side_effect = HTTPError(
            url="https://api.resend.com/emails",
            code=401,
            msg="Unauthorized",
            hdrs={},
            fp=err_stream
        )

        ok, msg = send_email_smtp("Subject", "Body")
        self.assertFalse(ok)
        self.assertIn("401", msg)
        self.assertIn("Authentication failed", msg)
        self.assertIn("API key is invalid", msg)
        # Verify secret key is not in message
        self.assertNotIn("re_mock_test_key_xyz", msg)

    @patch("app.email_service.urlopen")
    def test_http_403_sandbox_restriction(self, mock_urlopen):
        """Verifies safe error handling for onboarding sandbox limitation (HTTP 403)."""
        err_stream = io.BytesIO(json.dumps({
            "statusCode": 403,
            "name": "validation_error",
            "message": "You can only send testing emails to your own email address (tejas2005patel@gmail.com)."
        }).encode("utf-8"))
        mock_urlopen.side_effect = HTTPError(
            url="https://api.resend.com/emails",
            code=403,
            msg="Forbidden",
            hdrs={},
            fp=err_stream
        )

        ok, msg = send_email_smtp("Subject", "Body")
        self.assertFalse(ok)
        self.assertIn("403", msg)
        self.assertIn("policy restriction", msg)
        self.assertIn("You can only send testing emails", msg)

    @patch("app.email_service.urlopen")
    def test_http_429_rate_limiting(self, mock_urlopen):
        """Verifies rate limit reporting for HTTP 429."""
        err_stream = io.BytesIO(json.dumps({
            "statusCode": 429,
            "message": "Too many requests"
        }).encode("utf-8"))
        mock_urlopen.side_effect = HTTPError(
            url="https://api.resend.com/emails",
            code=429,
            msg="Too Many Requests",
            hdrs={},
            fp=err_stream
        )

        ok, msg = send_email_smtp("Subject", "Body")
        self.assertFalse(ok)
        self.assertIn("429", msg)
        self.assertIn("Rate limit exceeded", msg)

    @patch("app.email_service.urlopen")
    def test_network_gaierror(self, mock_urlopen):
        """Verifies network resolution failure handling without crash."""
        mock_urlopen.side_effect = URLError(socket.gaierror(8, "nodename nor servname provided, or not known"))

        ok, msg = send_email_smtp("Subject", "Body")
        self.assertFalse(ok)
        self.assertIn("Network connection error", msg)
        self.assertIn("nodename nor servname provided", msg)

    @patch("app.email_service.urlopen")
    def test_ssl_certificate_verification_error(self, mock_urlopen):
        """Verifies SSL certificate error handling."""
        mock_urlopen.side_effect = URLError(ssl.SSLCertVerificationError(1, "[SSL: CERTIFICATE_VERIFY_FAILED] verify failed"))

        ok, msg = send_email_smtp("Subject", "Body")
        self.assertFalse(ok)
        self.assertIn("TLS certificate verification error", msg)

    @patch("app.email_service.urlopen")
    def test_connection_timeout(self, mock_urlopen):
        """Verifies socket and urllib timeout handling."""
        mock_urlopen.side_effect = TimeoutError("The read operation timed out")

        ok, msg = send_email_smtp("Subject", "Body")
        self.assertFalse(ok)
        self.assertIn("timed out", msg)

    def test_ssl_context_strict_verification(self):
        """Verifies that _get_ssl_context enforces CERT_REQUIRED and hostname verification."""
        ctx = _get_ssl_context()
        self.assertTrue(ctx.check_hostname)
        self.assertEqual(ctx.verify_mode, ssl.CERT_REQUIRED)


if __name__ == "__main__":
    unittest.main()
