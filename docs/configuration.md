# 🛠️ Configuration Manager Guide

The **QA Hub Framework** employs a robust, centralized configuration system designed to handle complex testing environments with ease. This guide explains how it works, how to use it, and how to implement it in your projects.

---

## 🏗️ How It Works

The core of this system is the `ConfigManager` singleton class. It automatically loads and merges configuration from multiple sources in a specific hierarchy, giving you fine-grained control over your test settings.

### Loading Hierarchy (Priority Order)

1.  **Environment Variables** (Highest Priority)
    -   System-level variables override *all* file-based settings.
    -   Example: `DRIVER_HEADLESS=false` overrides `headless: true` in YAML.

2.  **Secrets (`.env`)**
    -   Loaded from the project root.
    -   Used for sensitive data (API keys, passwords) that should *never* be committed to Git.
    -   Overrides YAML files.

3.  **Environment-Specific Config (`features/config/config.{env}.yaml`)**
    -   Loaded only if the `ENV` environment variable is set (e.g., `ENV=staging`).
    -   Used to override base settings for specific environments (URL, timeout, accounts).

4.  **Base Config (`features/config/config.yaml`)** (Lowest Priority)
    -   The default configuration file.
    -   Contains standard settings applicable to all runs unless rewritten.

---

## 📂 File Structure

Your project should follow this structure for configuration files:

```text
my-project/
├── .env                        # Secrets (GitIgnored)
├── features/
│   └── config/
│       ├── config.yaml         # Base configuration
│       ├── config.staging.yaml # Staging overrides
│       └── config.prod.yaml    # Production overrides
```

---

## 🚀 Usage Guide

### 1. Setting Up Base Configuration

Create `features/config/config.yaml`:

```yaml
# features/config/config.yaml
Driver:
  type: chrome
  headless: true
  window_width: 1920
  window_height: 1080

VisualTests:
  enabled: true
  fail: true
```

### 2. Defining Environment Overrides

Create `features/config/config.staging.yaml` for your Staging environment:

```yaml
# features/config/config.staging.yaml
Driver:
  # On staging, we might want to see the browser for debugging
  headless: false 

VisualTests:
  # Don't fail the build on visual diffs in staging yet
  fail: false
```

### 3. Managing Secrets

Create a `.env` file in your root directory:

```ini
# .env
API_KEY=12345-secret-key
DB_PASSWORD=super_secure_pass
```

### 4. Running Tests

Switching environments is as simple as setting the `ENV` variable:

```bash
# Run with defaults (config.yaml)
qa-hub run

# Run with Staging Config (config.yaml + config.staging.yaml)
ENV=staging qa-hub run

# Run with Production Config
ENV=prod qa-hub run
```

---

## 💻 Implementation Details (For Developers)

If you want to use the `ConfigManager` in your own code or steps:

```python
from qa_framework.core.config_manager import ConfigManager

# 1. Get the singleton instance
config = ConfigManager.instance()

# 2. Access variables using dot notation
browser_type = config.get("Driver.type") 
is_visual_enabled = config.get("VisualTests.enabled", default=False)

# 3. Access Env Vars automatically
# If API_KEY is in .env, this works:
api_key = config.get("API_KEY") 
```

### Key Benefits

1.  **No Code Changes**: Switch environments without touching a single line of Python code.
2.  **Security**: Secrets are kept out of the codebase.
3.  **Clarity**: Inheritance model (`Base` -> `Env` -> `Var`) makes debugging configuration easy.
4.  **Scalability**: Add as many environments as you need (`qa`, `uat`, `preprod`).

---
