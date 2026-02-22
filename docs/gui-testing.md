<div align="center">
  <h1>🖱️ GUI Testing Guide</h1>
  <p><i>Advanced browser automation via unified Selenium and Playwright engines.</i></p>
</div>

---

The framework provides powerful Gherkin steps for browser automation, supporting both Selenium (standard) and Playwright (via wrapper) through a unified API.

## 🎭 Driver Configuration

Browser settings (headless mode, window size, browser type) are managed via `features/config/config.yaml`.

```yaml
Driver:
  type: chrome
  headless: true
```

For environment-specific overrides (e.g., debugging in Staging), see the [Configuration Guide](./configuration.md).

## compass Basic Navigation & Interactions

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
And I click on the "settings_icon"
```

---

## 🖱️ Advanced Interactions

### Mouse Actions
- `When I hover over the "{element}"`
- `When I double click on the "{element}"`

### Keyboard Support
Simulate key presses for complex forms or shortcuts:
- `When I press the "Enter" key`
- `When I press the "Escape" key`
- `When I press the "Tab" key`

---

## 🔲 Window & Frame Management

Handle multiple tabs, iframes, and native browser alerts seamlessly.

- **Tabs**: `When I switch to the next tab` and `When I close the current tab`.
- **Iframes**: `When I switch to the iframe "{element}"` and `When I switch back to the default content`.
- **Alerts**: `When I accept the alert`.

---

## ✅ Advanced Validations

Go beyond simple visibility checks:

- **Attributes**: `Then the "submit_btn" should have the attribute "disabled" with value "true"`
- **URL**: `Then the URL should contain "/v2/dashboard"`
- **State**: `Then the "loading_spinner" should be hidden`

---

## 📸 Visual Regression Testing

Verify UI consistency using pixel-based comparison against verified baselines.

### Match with Thresholds
For dynamic environments, allow for minor rendering differences:
```gherkin
Then the "Charts" page should visually match "dashboard_snapshot" with a 5.0% tolerance
```

!!! note "Artifact Integration"
    Screenshots are automatically saved to the `screenshots/` directory and embedded as Base64 images in HTML reports.

---

## 🔄 Common Utilities

### Variable Storage
Extract data from the UI to use in subsequent steps (even in API steps!):
```gherkin
When I store the text of the "order_id_label" as "OrderID"
And I navigate to "/api/v1/orders/${OrderID}"
```

### Synchronization
- `wait_for_visible()`: Ensures the element is in DOM and clickable.
- `wait_for_clickable()`: Ensures the element is enabled.
- `wait_for_title()`: Waits for page transitions.

!!! tip "Explicit Timing"
    While discouraged, you can use `When I wait for 2 seconds` for handling tricky animations.
