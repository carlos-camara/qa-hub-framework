<div align="center">
  <h1>📝 Professional Logging</h1>
  <p><i>High-fidelity audit trails and contextual debugging for global execution.</i></p>
</div>

---

The framework features a **ContextualLogger** designed for clear audit trails and high-fidelity debugging in both local and CI/CD environments.

## 🚀 Overview

Unlike standard `print` statements, the `ContextualLogger`:
- **Automatically detects context**: Extracts Feature and Scenario names from Behave.
- **Color-coded output**: Standardized colors for different severity levels.
- **Audit-ready**: Prepend every log with a high-precision timestamp.
- **Terminal Friendly**: Uses ANSI codes for beautiful terminal formatting.

## 📊 Log Levels

| Level | Color | Usage |
| :--- | :--- | :--- |
| `info` | 🔵 Blue | General progress, navigation, request sending. |
| `success` | 🟢 Green | Key milestones or successful assertions. |
| `warning` | 🟡 Yellow | Deprecated steps, explicit waits, or unusual states. |
| `error` | 🔴 Red | Critical failures, environmental issues. |
| `debug` | ⚪ Gray | Verbose data, variable storage, internal state. |

## 🛠️ Usage in Steps

The logger is readily available inside step definitions. Just import it and pass the `context` object to enable automatic context detection.

```python
from qa_framework.utils.logger import ContextualLogger

@when('I do something important')
def step_example(context):
    ContextualLogger.info("Starting important action...", context)
    # ... logic ...
    ContextualLogger.success("Action completed successfully!", context)
```

### Automatic Context Extraction
When you pass `context` to a log method, the logger will automatically prepend the output with:
`[FeatureName | ScenarioName]`

**Output Example:**
`19:29:45 [Billing | Process Invoice] INFO: Starting important action...`

---

## 🎨 Aesthetic Headers

For major sections or debugging blocks, use the `section` method:

```python
ContextualLogger.section("Response JSON")
print(json.dumps(data, indent=2))
```

!!! tip "CI/CD Integration"
    In GitHub Actions or Jenkins, these logs will be much easier to scan than white-on-black text, allowing you to quickly identify which scenario was running when an error occurred.
