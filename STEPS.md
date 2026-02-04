# 📔 Gherkin Steps Library

This library documents the **reusable common steps** provided by the framework. These steps are organized by component to help you build comprehensive test suites.

---

## 🌐 API Testing (`api_steps.py`)

Standardized steps for REST API validation, supporting dynamic variables, complex JSON assertions, and file uploads.

### Navigation & Setup
- `Given the API base URL is "{base_url}"`: Sets the target host.
- `When I set request headers`: Takes a table of key-value pairs (no trailing colon).

### Requests & Uploads
- `When I send a "{method}" request to "{path}"`: Simple HTTP call.
- `When I send a "{method}" request to "{path}" with query parameters`: Uses a Behave table.
- `When I send a "{method}" request to "{path}" with JSON body`: Uses a docstring for the payload.
- `When I send a "POST" request to "{path}" with form data`: For `x-www-form-urlencoded`.
- `When I upload the file "{filename}" to "{endpoint}"`: Generic multipart/form-data upload.

### Assertions & Variables
- `Then the response status code should be {status_code:d}`: Standard status check.
- `Then the response JSON path "{path}" should be "{expected}"`: Dot-notation JSON validation.
- `Then the response JSON path "{path}" should be {expected:d}`: Integer validation.
- `Then the response JSON path "{path}" should be a "{py_type}"`: Type check (str, int, float, bool, dict, list).
- `Then the response JSON path "{path}" should contain "{substring}"`: Substring matching.
- `Then the response JSON path "{path}" should be >= {value:d}`: Numeric comparison.
- `Then the response JSON path "{path}" should match regex "{pattern}"`: Regular expression matching.
- `Then the response JSON path "{path}" should be null`: Explicit null check.
- `Then the response header "{header_name}" should be "{expected}"`: Case-insensitive header check.
- `Then the response body should be empty`: Verifies no body is returned.
- `Then the response time should be less than {ms:d} ms`: Performance guardrail.
- `Then I store the response JSON path "{path}" as "{var_name}"`: Capture values for reuse.
- `Then the stored variables "{var_a}" and "{var_b}" should be different`: Uniqueness check.
- `Then the response JSON path "{path}" should equal stored variable "{var_name}"`: Cross-request verification.

### Debugging
- `Then I print the response JSON`: Pretty-prints the response body.
- `Then I print the request headers`: Displays the sent headers for triage.

### Security Sanity Checks
- `Then the response should not leak server metadata`: Checks for version numbers in 'Server' and presence of 'X-Powered-By'.
- `Then the response should contain mandatory security headers`: Validates HSTS, CSP, X-Frame-Options, and X-Content-Type-Options.
- `Then all session cookies should be secure`: Audits cookies for Secure, HttpOnly, and SameSite (Lax/Strict) flags.

---

## 🖱️ GUI Testing (`gui_steps.py`)

Steps for web UI interaction and validation, including robust waits and visual captures.

### Interaction
- `Given I navigate to "{url}"`: Browser navigation.
- `When I click on the element with text "{text}"`: Generic text-based interaction.
- `When I click on the button with text "{button_text}"`: Specifically targets button elements.
- `When I scroll to the bottom of the page`: Dynamic page navigation.

### Validation
- `Then the page title should be "{expected_title}"`: Title verification.
- `Then I should see the text "{text}"`: Global page source check.
- `Then I should see an element with class "{class_name}"`: CSS-based visibility check.

### Visual Comparison & Regression
- `Then the "{description}" element should visually match the baseline image "{name}"`: Pixel-perfect match (0% tolerance).
- `Then the "{description}" page should visually match the baseline image "{name}" with a {threshold:f}% tolerance`: Configurable layout shift protection.

---

## 🏷️ Framework Tags

The framework supports specialized Behave tags to control driver lifecycle:

- `@reuse_driver`: Apply to a `Feature` to share a single browser session across all its scenarios.
- `@reset_driver`: Apply to a `Scenario` to force a browser restart, even if reuse is enabled globally.

---

### Visual Captures
- `Then I take a screenshot named "{screenshot_name}"`: Standard screenshot with HTML embedding support.

---

## 📄 PDF Testing (`pdf_steps.py`)

Specialized steps for verifying document downloads and content.

- `When I wait for {seconds:d} seconds for the download to complete`: Timing control.
- `Then the downloaded file "{filename}" should exist`: Integrity check.
- `Then the PDF "{filename}" should have at least {page_count:d} pages`: Structure check.
- `Then I verify the content of the first {count:d} pages of "{filename}" contains "{keyword}"`: Text-in-PDF validation.

---

## 🛠️ How to use these steps

To leverage these steps in your project, ensure your `environment.py` or steps directory imports them:

```python
# API Steps
from qa_framework.steps.api_steps import *

# GUI Steps
from qa_framework.steps.gui_steps import *

# PDF Steps
from qa_framework.steps.pdf_steps import *

# Common/Utility Steps (like 'I wait for N seconds')
from qa_framework.steps.common_steps import *
```

---

<p align="center">
  <i>Accelerating QA engineering with standardized building blocks.</i>
</p>
