"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           QA Hub Framework                                    ║
║                        Security Step Unit Tests                               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Tests for security sanity checks including:                                  ║
║  • Server metadata leak detection                                             ║
║  • Mandatory security header validation                                       ║
║  • Cookie security flag verification                                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import pytest
from unittest.mock import MagicMock
from qa_framework.steps.api_steps import (
    step_security_no_metadata_leaks,
    step_security_mandatory_headers,
    step_security_cookies
)

@pytest.fixture
def mock_context():
    context = MagicMock()
    context.response.headers = {}
    context.response.cookies = []
    return context

def test_no_metadata_leaks_success(mock_context):
    """✓ Should pass when Server and X-Powered-By are absent or generic."""
    mock_context.response.headers = {"Server": "nginx", "Content-Type": "application/json"}
    step_security_no_metadata_leaks(mock_context)

def test_metadata_leak_server_version(mock_context):
    """✖ Should fail when Server header contains a version number."""
    mock_context.response.headers = {"Server": "nginx/1.18.0"}
    with pytest.raises(AssertionError, match="Security Leak Detected: Server: nginx/1.18.0"):
        step_security_no_metadata_leaks(mock_context)

def test_metadata_leak_powered_by(mock_context):
    """✖ Should fail when X-Powered-By header is present."""
    mock_context.response.headers = {"X-Powered-By": "Express"}
    with pytest.raises(AssertionError, match="Security Leak Detected: X-Powered-By: Express"):
        step_security_no_metadata_leaks(mock_context)

def test_mandatory_headers_success(mock_context):
    """✓ Should pass when all security headers are present."""
    mock_context.response.headers = {
        "Strict-Transport-Security": "max-age=31536000",
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Content-Security-Policy": "default-src 'self'"
    }
    step_security_mandatory_headers(mock_context)

def test_mandatory_headers_missing(mock_context):
    """✖ Should fail when some security headers are missing."""
    mock_context.response.headers = {"X-Content-Type-Options": "nosniff"}
    with pytest.raises(AssertionError, match="Missing Security Headers: Strict-Transport-Security"):
        step_security_mandatory_headers(mock_context)

def test_secure_cookies_success(mock_context):
    """✓ Should pass when cookies have all security flags."""
    cookie = MagicMock()
    cookie.name = "session"
    cookie.secure = True
    cookie.httponly = True
    cookie.rest = {"SameSite": "Lax"}
    mock_context.response.cookies = [cookie]
    
    step_security_cookies(mock_context)

def test_insecure_cookies_failure(mock_context):
    """✖ Should fail when cookies miss security flags."""
    cookie = MagicMock()
    cookie.name = "session"
    cookie.secure = False
    cookie.httponly = False
    cookie.rest = {"SameSite": "None"}
    mock_context.response.cookies = [cookie]
    
    with pytest.raises(AssertionError, match="Insecure Cookies Detected"):
        step_security_cookies(mock_context)

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
