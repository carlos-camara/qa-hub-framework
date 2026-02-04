# 🖱️ GUI Testing

The framework provides powerful Gherkin steps for browser automation, supporting both Selenium (standard) and Playwright (via wrapper) through a unified API.

## 🧭 Basic Navigation & Interactions

Start your GUI scenarios by navigating to a URL and interacting with elements using natural language.

```gherkin
Given I navigate to "https://dashboard.example.com"
When I click on the button with text "Login"
And I scroll to the bottom of the page
Then I should see the text "Welcome back"
```

---

## 🏗️ Page Object Pattern

We use a **YAML-driven Page Object pattern**. This separates locators from test logic, allowing non-technical stakeholders to update locators without touching Python code.

### Locators Definition
```yaml
# features/page_objects/dashboard.yml
stats_panel:
  by: css
  value: ".stats-container"
  type: webelement
  wait_load: true  # Automatically waited for on page load
```

### Context-Aware Steps
By setting the "current page", you can write shorter, more readable steps:
```gherkin
Given the "dashboard" page is displayed
Then I should see the "stats_panel"
```

---

## 📸 Visual Regression Testing

Verify UI consistency using pixel-based comparison against verified baselines.

### Screenshot Capture
```gherkin
Then I take a screenshot named "login-page-state"
```

### Visual Match with Thresholds
For dynamic environments, allow for minor rendering differences:
```gherkin
Then the "Charts" page should visually match "dashboard_snapshot" with a 5.0% tolerance
```

!!! note "Artifact Integration"
    Screenshots are automatically saved to the `screenshots/` directory and embedded as Base64 images in HTML reports.

---

## 🛡️ Synchronization

The framework automatically handles common timing issues through driver-agnostic wait utilities:
- `wait_for_visible()`: Ensures the element is in DOM and clickable.
- `wait_for_clickable()`: Ensures the element is enabled.
- `wait_for_title()`: Waits for page transitons.

!!! tip "Performance"
    The framework uses optimized polling and explicit waits instead of `time.sleep()`, resulting in faster and more stable tests.
