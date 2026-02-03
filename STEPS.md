# 📔 Gherkin Steps Library

This library documents the **reusable common steps** provided by the framework. These steps are designed to be imported into any project to accelerate test development.

---

## 📂 Navigation & URL Verification

### `the page URL should contain "{url_fragment}"`
Verifies that the current browser URL contains the expected string.

| Parameter | Type | Description |
|-----------|------|-------------|
| `url_fragment` | `string` | The partial text expected in the URL. |

**Example:**
```gherkin
Then the page URL should contain "dashboard"
```

---

## 🔍 Validation & Assertions

### `I should see the text "{text}"`
Checks if the specified text is present anywhere in the current page source.

| Parameter | Type | Description |
|-----------|------|-------------|
| `text` | `string` | The text string to look for. |

**Example:**
```gherkin
Then I should see the text "Welcome back, Carlos"
```

---

## 🛠️ Utilities & Debugging

### `I wait for {seconds:d} seconds`
Executes an explicit sleep. Use this sparingly; prefer Page Object waits for better performance.

| Parameter | Type | Description |
|-----------|------|-------------|
| `seconds` | `int` | Number of seconds to pause execution. |

**Example:**
```gherkin
When I wait for 2 seconds
```

### `I take a screenshot named "{screenshot_name}"`
Captures the current browser state and saves it. If using an HTML report, it will automatically embed the image.

| Parameter | Type | Description |
|-----------|------|-------------|
| `screenshot_name` | `string` | The filename (without extension) for the capture. |

**Example:**
```gherkin
Then I take a screenshot named "after_login_success"
```

---

## 🛠️ How to use these steps

To leverage these steps in your project, ensure your `environment.py` or steps directory imports them:

```python
# In your features/steps/common_steps.py
from qa_framework.steps.common_steps import *
```

Once imported, you can use them directly in any `.feature` file without further implementation.

---

<p align="center">
  <i>Accelerating QA engineering with standardized building blocks.</i>
</p>
