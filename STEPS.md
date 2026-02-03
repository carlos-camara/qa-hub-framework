# 📔 Gherkin Steps Library

This library documents the **reusable common steps** provided by the framework. These steps are organized by component to help you build comprehensive test suites.

---

## 🌐 API Testing (`api_steps.py`)

Standardized steps for REST API validation, supporting dynamic variables and complex JSON assertions.

### Navigation & Setup
- `Given the API base URL is "{base_url}"`: Sets the target host.
- `When I set request headers`: Takes a table of key-value pairs.

### Requests
- `When I send a "{method}" request to "{path}"`: Simple HTTP call.
- `When I send a "{method}" request to "{path}" with query parameters`: Uses a Behave table.
- `When I send a "{method}" request to "{path}" with JSON body`: Uses a docstring for the payload.
- `When I send a "POST" request to "{path}" with form data`: For `x-www-form-urlencoded`.

### Assertions & Variables
- `Then the response status code should be {status_code:d}`: Standard status check.
- `Then the response JSON path "{path}" should be "{expected}"`: Dot-notation JSON validation.
- `Then the response time should be less than {ms:d} ms`: Performance guardrail.
- `Then I store the response JSON path "{path}" as "{var_name}"`: Capture values for reuse.

---

## �️ GUI Testing (`gui_steps.py`)

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
```

---

<p align="center">
  <i>Accelerating QA engineering with standardized building blocks.</i>
</p>
