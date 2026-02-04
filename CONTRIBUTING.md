# Contributing to QA Hub Framework

First off, thank you for considering contributing to the QA Hub Framework! It's people like you that make it a great tool for the community. 🎉

> [!NOTE]
> These are guidelines, not rigid rules. Use your best judgment and feel free to propose changes to this document.

## 🛠️ Development Environment Setup

Follow these steps to get your local environment ready for contribution.

### Prerequisites
* **Python**: 3.10 or higher
* **Git**: Latest version

### 1. Initialize the Core Framework
The framework is a Python package designed for reuse across automation projects.

```powershell
# Clone the repository
git clone https://github.com/your-username/qa-hub-framework.git
cd qa-hub-framework

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies and framework in editable mode
pip install -r requirements.txt
pip install -e .
```

---

## 🎨 Engineering Standards

### Python & BDD (Behave)
* **Code Style**: Follow **PEP 8** guidelines.
* **Typing**: Use type hints for function signatures and critical variables.
* **Docstrings**: Document all classes and functions following the Google Python Style Guide.
* **Step Definitions**: Maintain a modular structure for step definitions to ensure reusability.

---

## 🔄 The Contribution Workflow

1. **Find an Issue**: Browse the issues or create one to discuss your proposed change.
2. **Branching Strategy**:
   - Feature: `feat/amazing-feature`
   - Fix: `fix/critical-bug`
3. **Quality Check**:
   - Run a linter (e.g., `flake8` or `pylint`) to check for style issues.
   - Verify changes by running a test suite that consumes the framework (like the `dashboard` smoke tests).
4. **Submitting a Pull Request**:
   - Target the `main` branch.
   - Describe the change and its impact clearly.
   - Link the PR to the relevant issue.
   - **Note**: PRs are automatically labeled based on the files changed.

---

## 🐞 Reporting Bugs

> [!WARNING]
> Before reporting a bug, please search existing issues to see if it has already been reported.

When opening an issue, please provide:
* **Context**: What were you trying to achieve?
* **Reproduce**: Exact steps to trigger the bug.
* **Evidence**: Error logs, tracebacks, or screenshots.
* **Environment**: OS, Python version, and Selenium/Browser version (if applicable).

---
> Happy coding! 🚀
