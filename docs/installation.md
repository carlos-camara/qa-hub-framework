# 🛠️ Installation & Setup

Setting up the **QA Hub Framework** in your project is a straightforward process. The framework is designed to be easily integrated into any Python-based test automation project (specifically those using Behave).

## 📋 Prerequisites

- **Python 3.8+**
- **pip** (Python package installer)
- **Git** (for remote installation)

## 🚀 Installation via pip

The most common way to include the framework is by adding it as a dependency in your `requirements.txt` file or installing it directly via `pip`.

### Direct Installation
```bash
pip install git+https://github.com/carlos-camara/qa-hub-framework.git#egg=qa-automation-framework
```

### In requirements.txt
Add the following line to your project's `requirements.txt`:
```text
-e git+https://github.com/carlos-camara/qa-hub-framework.git#egg=qa-automation-framework
```
Then run:
```bash
pip install -r requirements.txt
```

## ⚙️ Initial Configuration

Once installed, you must tell Behave where to find the step definitions. In your project's `environment.py` (or individual step files), import the desired components:

```python
# Import all common components
from qa_framework.steps.api_steps import *
from qa_framework.steps.gui_steps import *
from qa_framework.steps.pdf_steps import *
from qa_framework.steps.common_steps import *
```

!!! tip "Selective Imports"
    If your project only performs API testing, you only need to import `api_steps`. This keeps your step registry clean and fast.
