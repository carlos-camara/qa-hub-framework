# Contributing to QA Hub Framework

Thank you for your interest in contributing to the **QA Hub Framework**! This document provides guidelines and best practices for contributing.

---

## 📋 Table of Contents

- [Getting Started](#-getting-started)
- [Development Workflow](#-development-workflow)
- [Engineering Standards](#-engineering-standards)
- [Pull Request Guidelines](#-pull-request-guidelines)
- [Code of Conduct](#-code-of-conduct)

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- pip and virtual environment support
- Git

### Setup

```bash
# Clone the repository
git clone https://github.com/carlos-camara/qa-hub-framework.git
cd qa-hub-framework

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -e .
pip install pytest flake8 pylint
```

---

## 🔄 Development Workflow

1. **Fork** the repository and create a feature branch
2. **Develop** your feature following the engineering standards
3. **Test** your changes locally
4. **Submit** a pull request using the PR template

### Branch Naming Convention

| Type | Format | Example |
|------|--------|---------|
| Feature | `feature/description` | `feature/add-select-element` |
| Bug Fix | `fix/description` | `fix/playwright-locator-conversion` |
| Documentation | `docs/description` | `docs/update-readme` |
| Refactor | `refactor/description` | `refactor/element-factory` |

---

## 🎨 Engineering Standards

### Code Style

- Follow **PEP 8** style guidelines
- Use **4 spaces** for indentation (no tabs)
- Maximum line length: **100 characters**
- Use **snake_case** for functions and variables
- Use **PascalCase** for class names

### Documentation

Every public function, class, and module must have docstrings:

```python
def create_element(driver, element_type, locator_data):
    """
    Create a typed element instance from configuration.
    
    Args:
        driver: WebDriver instance (Selenium or Playwright)
        element_type: Type identifier from YAML
        locator_data: Dictionary with 'by' and 'value' keys
        
    Returns:
        Typed element instance (Button, Input, etc.)
        
    Raises:
        ValueError: If element_type is unknown
    """
```

### Module Headers

Use ASCII art headers for major modules:

```python
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           QA Hub Framework                                    ║
║                         Module Description                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
```

### Testing

- Write unit tests for new functionality
- Ensure all existing tests pass before submitting
- Use descriptive test names that explain the scenario

### Linting

Run linting before committing:

```bash
# Check style
flake8 qa_framework/ --max-line-length=100

# Check code quality
pylint qa_framework/
```

---

## 📝 Pull Request Guidelines

1. **Use the PR Template**: Fill out all sections in the pull request template
2. **One Feature Per PR**: Keep PRs focused on a single change
3. **Descriptive Titles**: Use conventional commit format (e.g., `feat: add Select element class`)
4. **Link Issues**: Reference related issues with `Fixes #123`
5. **Update Documentation**: Include relevant doc updates in the same PR

### Commit Message Format

```
type: short description

Optional longer description explaining the change in detail.
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `style`

---

## 🤝 Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow
- Follow project conventions

---

Thank you for contributing! 🚀
