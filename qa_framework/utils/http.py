import json
import re
from typing import Any, Dict

# Matches placeholders like ${batch_id}
VAR_PATTERN = re.compile(r"\$\{([A-Za-z][A-Za-z0-9_]*)\}")

def parse_expected(value: str) -> Any:
    """
    Convert expected values to proper JSON types when possible.
    Examples:
      "1" -> 1
      "true" -> True
      "\"abc\"" -> "abc" (if user passes JSON string literal)
      "abc" -> "abc" (fallback)
    """
    if value is None:
        return None

    v = value.strip()

    # If it's already a JSON literal (number, object, array, true/false/null, or quoted string)
    try:
        return json.loads(v)
    except Exception:
        return v  # treat as plain string


def get_json_path(payload: Any, path: str) -> Any:
    """
    Minimal JSON-path via dot-notation:
      "args.foo" -> payload["args"]["foo"]
      "json.id"  -> payload["json"]["id"]
      "0.id"     -> payload[0]["id"] (if payload is a list)
    """
    if payload is None:
        raise AssertionError("Response JSON is empty / None")

    current = payload
    for part in path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        elif isinstance(current, list) and part.isdigit():
            index = int(part)
            if index < len(current):
                current = current[index]
            else:
                raise AssertionError(
                    f"JSON path index out of range: '{path}'. Index: {index}, List length: {len(current)}"
                )
        else:
            raise AssertionError(
                f"JSON path not found: '{path}'. Missing part: '{part}'. Current type: {type(current)}"
            )
    return current


def full_url(base: str, path: str) -> str:
    return base.rstrip("/") + "/" + path.lstrip("/")


def loads_json_or_fail(raw: str) -> Any:
    raw_body = (raw or "").strip()
    if not raw_body:
        raise AssertionError("JSON body was expected but step text is empty.")

    try:
        return json.loads(raw_body)
    except json.JSONDecodeError as e:
        raise AssertionError(f"Invalid JSON body provided. Error: {e}\nBody:\n{raw_body}") from e


def table_to_params(table) -> Dict[str, Any]:
    """
    Behave table expected format: | key | value |
    """
    params: Dict[str, Any] = {}
    for row in table:
        key = row[0].strip()
        value = row[1].strip()
        params[key] = parse_expected(value)
    return params


def table_to_form_including_headings(table):
    """
    Supports:
    - With headings: | Field | Value |
    - Without headings: first row treated as headings by Behave, so we include headings as data.
    """
    if table is None:
        return {}

    form = {}

    # If user did NOT provide headings, Behave treats first row as headings.
    # Include headings as first data row.
    if table.headings and len(table.headings) >= 2:
        h0 = str(table.headings[0]).strip()
        h1 = str(table.headings[1]).strip()
        # If headings look like actual columns (Field/Value), we DON'T treat them as data.
        if not (h0.lower() in ("field", "key", "name") and h1.lower() in ("value", "val")):
            form[h0] = h1

    # Remaining rows
    for row in table:
        form[str(row[0]).strip()] = str(row[1]).strip()

    return form

def get_header_case_insensitive(headers: dict, name: str):
    """
    Returns the value of a header from a headers dict using case-insensitive matching.
    """
    name_l = name.lower()
    for k, v in headers.items():
        if k.lower() == name_l:
            return v

    # If not found, provide a helpful error with the headers we actually received
    raise AssertionError(f"Header '{name}' not found. Available: {list(headers.keys())}")


def substitute_vars(raw: str, variables: dict) -> str:
    """
    Replaces ${var} placeholders using values stored in context.vars.
    """
    def repl(match):
        key = match.group(1)
        if key not in variables:
            raise AssertionError(
                f"Variable '{key}' not found in context.vars. "
                f"Set it first (e.g., store it from a previous response)."
            )
        return str(variables[key])

    return VAR_PATTERN.sub(repl, raw)
