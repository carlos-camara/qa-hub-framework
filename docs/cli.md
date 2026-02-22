<div align="center">
  <h1>🛠️ Command Line Interface</h1>
  <p><i>Empowering surgical test execution via the `qa-hub` binary.</i></p>
</div>

---

The framework provides a dedicated Command Line Interface to simplify test execution and environment management.

## 🚀 Getting Started

Once the framework is installed, you can use the `qa-hub` command from any terminal.

```bash
# Verify installation
qa-hub --help
```

## 🏃 Commands

### `run`
Executes the test suite using `behave` internally but with streamlined arguments.

| Argument | Description | Default |
| :--- | :--- | :--- |
| `--env` | Target environment (e.g., `staging`, `prod`, `dev`) | `local` |
| `--tags` | Filter scenarios by Gherkin tags (e.g., `@smoke`) | `None` |
| `--browser` | Specify browser (e.g., `chrome`, `firefox`, `playwright`) | `None` |
| `--fail` | Stop execution immediately on the first failure | `False` |
| `--no-capture` | Show `print` statements and logs in real-time | `False` |
| `--path` | Path to the directory containing feature files | `features` |
| `--junit-dir` | Directory to store JUnit XML reports | `None` |

## 💡 Examples

**1. Run smoke tests in staging:**
```bash
qa-hub run --env staging --tags smoke
```

**2. Debugging a specific feature with real-time logs:**
```bash
qa-hub run --path features/login.feature --no-capture
```

**3. CI/CD Integration with dynamic reporting:**
```bash
qa-hub run --junit-dir reports/test_run/dashboard_$(date +%s)
```

---

## 🔧 Internal Mapping
The `qa-hub` tool automatically maps your arguments to the underlying `behave` configuration. For example:
`qa-hub run --env prod` → `python -m behave -D env=prod`

This ensures consistency across different developer environments and CI/CD pipelines.
