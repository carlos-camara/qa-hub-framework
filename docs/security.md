# 🛡️ Security Sanity Checks

The framework includes dedicated steps to verify basic security best practices in your API responses. These checks help ensure that your application doesn't leak sensitive information and follows industry-standard security header configurations.

## 🚀 Key Features

### 1. Metadata Leak Prevention
Prevents your server from leaking technology versions (e.g., `nginx/1.2.3`) which can be used by attackers to find specific vulnerabilities.

**Step:**
`Then the response should not leak server metadata`

*   **Checks:** Fails if `Server` contains a version number or if `X-Powered-By` is present.

### 2. Mandatory Security Headers
Ensure that your API provides the necessary headers to protect users from common web attacks.

**Step:**
`Then the response should contain mandatory security headers`

*   **Verified Headers:**
    *   `Strict-Transport-Security` (HSTS): Prevents Man-in-the-Middle attacks.
    *   `X-Content-Type-Options: nosniff`: Prevents MIME-sniffing.
    *   `X-Frame-Options`: Protects against Clickjacking.
    *   `Content-Security-Policy` (CSP): Mitigates XSS and data injection.

### 3. Session Cookie Security
Verify that your session cookies are properly protected for transmission over the network.

**Step:**
`Then all session cookies should be secure`

*   **Verified Flags:**
    *   `Secure`: Ensures the cookie is only sent over HTTPS.
    *   `HttpOnly`: Prevents client-side scripts from accessing the cookie.
    *   `SameSite`: (Lax/Strict) Protects against CSRF attacks.

## 💡 Example Scenario

```gherkin
Scenario: Validate API Security Posture
  Given the API base URL is "https://api.myapp.com"
  When I send a "GET" request to "/v1/status"
  Then the response status code should be 200
  And the response should not leak server metadata
  And the response should contain mandatory security headers
  And all session cookies should be secure
```

---

!!! success "Audit Ready"
    Using these steps in your Smoke or Regression suites provides a continuous security audit of your environment, alerting you instantly if a server misconfiguration occurs.
