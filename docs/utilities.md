# Utility Handlers

The framework includes several specialized handlers to manage dynamic data, visual regression, and common HTTP operations.

## Variable Handler

The `VariableHandler` enables dynamic data generation and token resolution within Gherkin steps. It supports several built-in generators that can be used directly in feature files.

### Supported Tokens

| Token | Example Result | Description |
| :--- | :--- | :--- |
| `[UUID]` | `550e8400-e2...` | Generates a unique Version 4 UUID. |
| `[RANDOM]` | `849203` | Generates a random 6-digit integer. |
| `[NOW]` | `2024-05-20` | Current date in YYYY-MM-DD. |
| `[NOW(%H:%M)]` | `14:30` | Current time with custom format. |
| `[STRING_10]` | `aB3dE...` | Random alphanumeric string of length 10. |

!!! example "Usage in Gherkin"
    ```gherkin
    When I type "[UUID]" into the "order_id"
    And I type "[STRING_20]" into the "description"
    ```

---

## Visual Handler

High-fidelity visual regression testing using pixel-by-pixel comparison with RMS (Root Mean Square) error detection.

### Key Features
- **Auto-Seeding**: If a baseline doesn't exist, the first run automatically saves the current screenshot as the baseline.
- **Threshold Control**: Configure tolerance for anti-aliasing or minor rendering differences.
- **Failing Strategy**: Tests fail automatically if similarity falls below the threshold.

### Configuration
Visual testing is controlled via the `VisualTests` section in `features/config/config.yaml`:

```yaml
VisualTests:
  enabled: true
  save: false      # Set to true to update all baselines
  fail: true       # Fail test on mismatch
  baseline_name: "{Driver_type}" # Environment-specific baseline prefix
```

The framework automatically loads these settings into `context.visual_config`.

---

## HTTP Utilities

The `HttpUtils` module provides logic for API test assertions and data parsing.

### JSON Path Navigation
Simple dot-notation to extract values from complex response payloads:
`data.users.0.email` → Navigates dicts and arrays.

### Type Parsing
Smart conversion from Gherkin "string" tables to proper JSON types:
- `"true"` → `True` (bool)
- `"123"` → `123` (int)
- `null` → `None` (NoneType)

!!! check "Professional Formatting"
    These utilities are designed to be "invisible" to the test writer, providing a seamless experience while maintaining high technical standard.
