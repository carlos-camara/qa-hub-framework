<div align="center">
  <h1>🚀 POM Migration Guide</h1>
  <p><i>Transitioning to the high-performance, typed element YAML format.</i></p>
</div>

---

## Evolution Overview
This guide covers the migration from basic locator structures to the robust, typed element framework.

## OLD FORMAT (Legacy Support)
```yaml
test_runs:
  title:
    by: xpath
    value: "//*[contains(text(), 'Execution Archives')]"
  search_input:
    by: xpath
    value: "//input[@placeholder='Search by project identifier, run ID, or tags...']"
  project_card:
    by: xpath
    value: "//*[@data-testid='project-card']"
```

## NEW FORMAT (recommended)
```yaml
test_runs:
  texts:
    title:
      by: xpath
      value: "//*[contains(text(), 'Execution Archives')]"
  
  inputs:
    search_input:
      by: xpath
      value: "//input[@placeholder='Search by project identifier, run ID, or tags...']"
  
  buttons:
    project_card:
      by: xpath
      value: "//*[@data-testid='project-card']"
    view_analytics_button:
      by: xpath
      value: "//*[contains(text(), 'View Analytics')]"
    delete_project_button:
      by: xpath
      value: "//button[contains(., 'Delete Project')]"
```

## Benefits of New Format
- ✅ Clear element types without redundancy
- ✅ Elements grouped by type for better organization
- ✅ Type-specific methods available (button.click(), input.type(), text.get_text())
- ✅ Better IDE autocomplete and type hints
- ✅ More maintainable and readable

## Migration Steps
1. Group elements by their type (buttons, inputs, texts)
2. Move each element under its corresponding section
3. Keep the same 'by' and 'value' structure
4. Test that all scenarios still pass

## Available Element Types
- `buttons` - Clickable elements (Button class)
- `inputs` - Text input fields (Input class)
- `texts` - Read-only text elements (Text class)
- `webelements` - Generic elements (WebElement class, fallback)
