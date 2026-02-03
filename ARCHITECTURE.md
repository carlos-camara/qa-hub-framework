# 🏗️ Framework Architecture

This document provides a deep dive into the internal structure and design decisions of the **QA Hub Framework**.

## 🧩 Core Components

### 1. BasePage (`qa_framework.core.base_page`)
The `BasePage` class is the foundation of our Page Object Model. It encapsulates common Selenium operations with built-in explicit waits.

**Key Methods:**
- `find_element(locator, timeout)`: Safe element retrieval with error handling.
- `click(locator)`: Waits for element to be clickable before interacting.
- `send_keys(locator, text)`: Safely inputs text after clearing the field.
- `is_visible(locator)`: Verification utility for assertions.

### 2. Driver Factory (`qa_framework.utils.driver`)
Centralizes the creation of the WebDriver instance.

**Features:**
- Standard Chrome options for stability.
- Headless mode toggle for local vs CI execution.
- Sandboxing and GPU disabling for Docker compatibility.

### 3. Common Steps (`qa_framework.steps.common_steps`)
A collection of reusable Behave steps that can be shared across multiple feature files to avoid duplication.

---

## 🛠️ Design Patterns

### Page Object Model (POM)
By separating the UI structure (Locators and Page Objects) from the test logic (Steps and Features), we achieve:
- **High Maintainability**: UI changes only require updates in one place.
- **Improved Readability**: Tests read like natural language.

### Explicit vs Implicit Waits
The framework prioritizes **Explicit Waits** via `WebDriverWait` to ensure tests are fast and reliable, avoiding the pitfalls of arbitrary sleep times.

---

## 🚀 Environment Compatibility

The framework is tested and optimized for:
- **Local Development**: Windows/Mac with GUI.
- **CI/CD Pipelines**: Linux runners (Ubuntu) using headless Chrome.
- **Docker**: Containerized execution with `--no-sandbox` enabled by default.
