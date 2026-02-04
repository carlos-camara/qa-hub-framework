# Testing the Framework

The QA Hub Framework is built with a "Test-First" mindset. We maintain a comprehensive suite of unit tests to ensure stability across version updates.

## Suite Overview

We use **Pytest** along with **unittest.mock** to isolate framework logic from external dependencies like real browsers or live APIs.

| File | Coverage Area |
| :--- | :--- |
| `test_elements.py` | Validates all 8+ element types and their semantic methods. |
| `test_gui_steps.py` | Verifies Gherkin step logic and wait utilities. |
| `test_api_steps.py` | Tests API assertion logic and status code handling. |
| `test_variable_handler.py` | Exhaustive testing of token generation and resolution. |
| `test_visual_handler.py` | Validates image comparison math and baseline management. |

---

## Running Tests

Execute the full suite from the root directory:

```bash
# Standard run
python -m pytest tests/

# Verbose run with summary
python -m pytest tests/ -v --tb=short
```

---

## Testing Standards

When adding new features or elements, follow these guidelines:

### 1. Mock Everything
Use the fixtures defined in `conftest.py` to avoid starting real browser sessions during unit testing.
```python
def test_new_feature(mock_driver, mock_context):
    # Use mocks to simulate browser behavior
    pass
```

### 2. ASCII Professionalism
Maintain the quality of the codebase by including our signature ASCII headers in new test files.

### 3. Assertion Quality
Always provide meaningful error messages in assertions to simplify debugging for other contributors.

!!! success "Continuous Integration"
    These tests are automatically executed on every Pull Request via GitHub Actions to prevent regressions.
