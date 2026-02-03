# 🚀 QA Hub Framework

Welcome to the official documentation for the **QA Hub Framework**.

This framework is built to accelerate quality engineering by providing a set of standardized, reusable building blocks for API, GUI, and PDF automation.

## ✨ Key Features

- **🌐 Unified API Automation**: Standardized steps for REST validation with dot-notation JSON path support.
- **🖱️ Robust GUI Testing**: Pre-built Selenium interactions with smart waits and visual validation.
- **📄 Advanced PDF Verification**: Automated document download and content integrity checks.
- **📔 Gherkin-First**: Focused on readable, maintainable, and collaborative test scenarios.
- **🛠️ Extensible Architecture**: Easily add project-specific steps while leveraging the core common library.

## 🏁 Quick Start

To begin using the framework in your project, install it via the remote repository:

```bash
pip install git+https://github.com/carlos-camara/qa-hub-framework.git#egg=qa-automation-framework
```

Then, import the steps into your `environment.py` or steps directory:

```python
from qa_framework.steps.api_steps import *
from qa_framework.steps.gui_steps import *
```

---

<p align="center">
  <i>Empowering engineers to build better software, faster.</i>
</p>
