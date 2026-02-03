# 🖱️ GUI Testing

Web automation is powered by Selenium, providing a high-level Gherkin interface that abstracts away the complexity of handling browser drivers and elements.

## 🧭 Navigation

Start your GUI scenarios by navigating to a URL:
```gherkin
Given I navigate to "https://dashboard.example.com"
```

## ⚡ Interactions

The framework focuses on readable interactions that don't require complex CSS selectors in your Gherkin.

### Clicking Elements
```gherkin
When I click on the element with text "Submit"
When I click on the button with text "Login"
```

### Scrolling
```gherkin
When I scroll to the bottom of the page
```

## 🔍 Validation

### Basic Checks
```gherkin
Then the page title should be "Dashboard | QA Hub"
Then I should see the text "Welcome back, Carlos"
Then I should see an element with class "status-indicator--online"
```

## 📸 Visual Validation

Automated screenshots are crucial for failure analysis and UI regression checks.

```gherkin
Then I take a screenshot named "login-page-state"
```

!!! note "Artifact Integration"
    Screenshots are automatically saved to the `screenshots/` directory and embedded as Base64 images if your Behave formatter supports it (like the HTML formatter).
