"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           QA Hub Framework                                    ║
║                          API Step Definitions                                 ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  This module contains all Gherkin step definitions for REST API testing.    ║
║                                                                              ║
║  Features:                                                                    ║
║  • RESTful requests (GET, POST, PUT, DELETE, etc.)                           ║
║  • JSON Path assertions (dot-notation support)                               ║
║  • Token-based dynamic data resolution                                       ║
║  • Multipart file uploads and Form data                                      ║
║  • Header management and timing assertions                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
from behave import given, when, then
import requests
import re
import json
import os
from qa_framework.utils.http import (
    full_url,
    loads_json_or_fail,
    table_to_params,
    table_to_form_including_headings,
    substitute_vars,
    parse_expected,
    get_json_path,
    get_header_case_insensitive
)
from qa_framework.utils.logger import ContextualLogger

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1: REQUEST CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

@given('the API base URL is "{base_url}"')
def step_set_base_url(context, base_url: str):
    """Set the root endpoint for all subsequent API requests."""
    context.base_url = base_url
    context.response = None
    context.response_json = None
    context.last_request = None

@when("I set request headers")
def step_set_request_headers(context):
    """Set common headers using a table: | key | value |"""
    if context.table is None:
        raise AssertionError("This step requires a table.")
    if not hasattr(context, "default_headers") or context.default_headers is None:
        context.default_headers = {}
    new_headers = table_to_params(context.table)
    context.default_headers.update(new_headers)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2: SENDING REQUESTS
# ═══════════════════════════════════════════════════════════════════════════════

@when('I send a "{method}" request to "{path}"')
def step_send_request_simple(context, method: str, path: str):
    """Send a request without body or query parameters."""
    context.vars = getattr(context, "vars", {}) or {}
    resolved_path = substitute_vars(path, context.vars) if "${" in path else path
    url = full_url(context.base_url, resolved_path)
    method_u = method.upper()
    context.last_request = {"method": method_u, "url": url, "params": None, "json": None}
    if not hasattr(context, "default_headers") or context.default_headers is None:
        context.default_headers = {}
    
    ContextualLogger.info(f"Sending {method_u} request to: {url}", context)
    resp = requests.request(method=method_u, url=url, headers=context.default_headers, timeout=20)
    context.response = resp
    try:
        context.response_json = resp.json()
    except Exception:
        context.response_json = None

@when('I send a "{method}" request to "{path}" with query parameters')
def step_send_request_with_query(context, method: str, path: str):
    """Send a request with URL query parameters defined in a table."""
    url = full_url(context.base_url, path)
    method_u = method.upper()
    params = {}
    context.vars = getattr(context, "vars", {}) or {}
    if context.table:
        if len(context.table.headings) >= 2:
            h_key = context.table.headings[0].strip()
            h_val = context.table.headings[1].strip()
            if h_key.lower() not in ("field", "key", "name", "parameter") or h_val.lower() not in ("value", "val"):
                if "${" in h_val:
                    h_val = substitute_vars(h_val, context.vars)
                params[h_key] = parse_expected(h_val)
        for row in context.table:
            key = row[0].strip()
            val_raw = row[1].strip()
            if "${" in val_raw:
                val_raw = substitute_vars(val_raw, context.vars)
            params[key] = parse_expected(val_raw)
    context.last_request = {"method": method_u, "url": url, "params": params, "json": None}
    if not hasattr(context, "default_headers") or context.default_headers is None:
        context.default_headers = {}
    resp = requests.request(method=method_u, url=url, headers=context.default_headers, params=params, timeout=20)
    context.response = resp
    try:
        context.response_json = resp.json()
    except Exception:
        context.response_json = None

@when('I send a "{method}" request to "{path}" with JSON body')
def step_send_request_with_json_body(context, method: str, path: str):
    """Send a request with a raw JSON body from the step text block."""
    url = full_url(context.base_url, path)
    method_u = method.upper()
    body = loads_json_or_fail(context.text)
    context.last_request = {"method": method_u, "url": url, "params": None, "json": body}
    if not hasattr(context, "default_headers") or context.default_headers is None:
        context.default_headers = {}
    resp = requests.request(method=method_u, url=url, headers=context.default_headers, json=body, timeout=20)
    context.response = resp
    try:
        context.response_json = resp.json()
    except Exception:
        context.response_json = None

@when('I send a "POST" request to "{path}" with form data')
def step_post_with_form_data(context, path: str):
    """Send a POST request with multipart/form-data."""
    if not hasattr(context, "default_headers") or context.default_headers is None:
        context.default_headers = {}
    url = full_url(context.base_url, path)
    form = table_to_form_including_headings(context.table)
    resp = requests.post(url, data=form, headers=context.default_headers, timeout=20)
    context.response = resp
    try:
        context.response_json = resp.json()
    except Exception:
        context.response_json = None
    context.last_request = {"method": "POST", "url": url, "headers": dict(context.default_headers), "form": form}

@when('I upload the file "{filename}" to "{endpoint}"')
def step_upload_file(context, filename, endpoint):
    """Upload a file to the specified endpoint."""
    possible_paths = [filename, os.path.join("features", "resources", filename),
                      os.path.join("features", "data", filename), os.path.join("test_data", filename)]
    file_path = next((p for p in possible_paths if os.path.exists(p)), None)
    if not file_path: raise FileNotFoundError(f"File '{filename}' not found.")
    url = full_url(context.base_url, endpoint)
    with open(file_path, 'rb') as f:
        files = {'files': (os.path.basename(file_path), f)}
        headers = getattr(context, "default_headers", {}).copy()
        if 'Content-Type' in headers: del headers['Content-Type']
        resp = requests.post(url, files=files, headers=headers, timeout=30)
        context.response = resp
        try: context.response_json = resp.json()
        except: context.response_json = None

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3: HTTP STATUS & BODY ASSERTIONS
# ═══════════════════════════════════════════════════════════════════════════════

@then("the response status code should be {status_code:d}")
def step_assert_status(context, status_code: int):
    """Verify the HTTP status code."""
    assert context.response is not None, "No response found."
    actual = context.response.status_code
    assert actual == status_code, f"Expected {status_code}, got {actual}. Body: {context.response.text[:500]}"

@then("the response body should be empty")
def step_response_body_empty(context):
    """Verify the response body is zero-length."""
    assert context.response is not None, "No response found."
    assert context.response.text.strip() == "", "Expected empty body."

@then("the response time should be less than {ms:d} ms")
def step_assert_time(context, ms: int):
    """Verify the response time is within limits."""
    assert context.response is not None, "No response found."
    elapsed_ms = context.response.elapsed.total_seconds() * 1000.0
    assert elapsed_ms < ms, f"Response time too high: {elapsed_ms:.2f} ms (limit: {ms} ms)"

@then('the response header "{header_name}" should be "{expected}"')
def step_assert_response_header(context, header_name: str, expected: str):
    """Verify a specific response header value."""
    assert context.response is not None, "No response found."
    headers = context.response_json.get("headers", {}) if context.response_json and isinstance(context.response_json, dict) else context.response.headers
    actual = get_header_case_insensitive(headers, header_name)
    assert actual == expected, f"Expected {expected}, got {actual}"

@then('the response header "{header_name}" should contain "{expected}"')
def step_assert_response_header_contains(context, header_name: str, expected: str):
    """Verify a response header contains a substring."""
    assert context.response is not None, "No response found."
    headers = context.response.headers
    actual = get_header_case_insensitive(headers, header_name)
    assert expected in actual, f"Expected '{expected}' to be in '{actual}'"

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4: JSON PATH ASSERTIONS (VALUES & TYPES)
# ═══════════════════════════════════════════════════════════════════════════════

@then('the response JSON path "{path}" should be "{expected}"')
def step_assert_json_path_str(context, path: str, expected: str):
    """Verify a JSON value matches a string or parsed type."""
    assert context.response_json is not None, "Response JSON is empty."
    actual = get_json_path(context.response_json, path)
    exp = parse_expected(expected)
    assert actual == exp, f"JSON mismatch at '{path}'. Expected: {exp}, Actual: {actual}"

@then('the response JSON path "{path}" should be {expected:d}')
def step_assert_json_path_int(context, path: str, expected: int):
    """Verify a JSON value matches an integer."""
    assert context.response_json is not None, "Response JSON is empty."
    actual = get_json_path(context.response_json, path)
    assert actual == expected, f"JSON mismatch at '{path}'. Expected: {expected}, Actual: {actual}"

@then('the response JSON path "{path}" should be a "{py_type}"')
def step_assert_json_type(context, path: str, py_type: str):
    """Verify the Python type of a JSON value (str, int, float, bool, dict, list)."""
    assert context.response_json is not None, "Response JSON is empty."
    val = get_json_path(context.response_json, path)
    mapping = {"str": str, "int": int, "float": float, "bool": bool, "dict": dict, "list": list}
    if py_type not in mapping: raise AssertionError(f"Unsupported type '{py_type}'.")
    assert isinstance(val, mapping[py_type]), f"Expected {py_type}, got {type(val)}"

@then('the response JSON path "{path}" should contain "{substring}"')
def step_assert_json_path_contains(context, path: str, substring: str):
    """Verify a JSON value string contains a substring."""
    assert context.response_json is not None, "Response JSON is empty."
    actual = get_json_path(context.response_json, path)
    assert substring in str(actual), f"Expected '{substring}' to be in '{actual}'"

@then('the response JSON path "{path}" should match regex "{pattern}"')
def step_json_path_matches_regex(context, path: str, pattern: str):
    """Verify a JSON value matches a regular expression."""
    assert context.response_json is not None, "Response JSON is empty."
    val = get_json_path(context.response_json, path)
    assert re.match(pattern, str(val)), f"Value '{val}' did not match regex '{pattern}'"

@then('the response JSON path "{path}" should be null')
def step_json_path_should_be_null(context, path: str):
    """Verify a JSON value is null/None."""
    assert context.response_json is not None, "Response JSON is empty."
    val = get_json_path(context.response_json, path)
    assert val is None, f"Expected null, got {val}"

@then('the response JSON path "{path}" should exist')
def step_json_path_exists(context, path: str):
    """Verify that a specific path exists in the response JSON."""
    assert context.response_json is not None, "Response JSON is empty."
    try:
        get_json_path(context.response_json, path)
    except AssertionError:
        raise AssertionError(f"JSON path '{path}' does not exist in response.")

@then('the response JSON path "{path}" should not exist')
def step_json_path_not_exists(context, path: str):
    """Verify that a specific path does NOT exist in the response JSON."""
    assert context.response_json is not None, "Response JSON is empty."
    exists = True
    try:
        get_json_path(context.response_json, path)
    except AssertionError:
        exists = False
    
    assert not exists, f"JSON path '{path}' was found but should not exist."

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5: JSON LIST & OBJECT ASSERTIONS
# ═══════════════════════════════════════════════════════════════════════════════

@then('the response JSON should have {count:d} elements')
def step_assert_json_count(context, count: int):
    """Verify the number of elements in the root JSON (list or dict)."""
    assert context.response_json is not None, "Response JSON is empty."
    actual = len(context.response_json)
    assert actual == count, f"Expected {count} elements, found {actual}"

@then('the response JSON path "{path}" should have {count:d} elements')
def step_assert_json_path_count(context, path: str, count: int):
    """Verify the number of elements in a list/dict at the specified path."""
    assert context.response_json is not None, "Response JSON is empty."
    val = get_json_path(context.response_json, path)
    actual = len(val)
    assert actual == count, f"Expected {count} elements at '{path}', found {actual}"

@then('the response JSON should be an array')
def step_assert_json_is_array(context):
    """Verify the root JSON is an array (list)."""
    assert isinstance(context.response_json, list), f"Expected array, got {type(context.response_json)}"

@then('the response JSON should be an object')
def step_assert_json_is_object(context):
    """Verify the root JSON is an object (dict)."""
    assert isinstance(context.response_json, dict), f"Expected object, got {type(context.response_json)}"

@then('the response JSON should not be empty')
def step_assert_json_not_empty(context):
    """Verify the response JSON contains at least one element."""
    assert context.response_json is not None, "Response JSON is None."
    assert len(context.response_json) > 0, "Response JSON is empty."

@then('the response JSON should contain keys')
def step_assert_json_contains_keys(context):
    """Verify root JSON dictionary contains specific keys (from table)."""
    assert isinstance(context.response_json, dict), "Response JSON is not a dictionary."
    if context.table:
        for row in context.table:
            key = row[0]
            assert key in context.response_json, f"Key '{key}' not found in response JSON."

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6: MATHEMATICAL COMPARISONS
# ═══════════════════════════════════════════════════════════════════════════════

@then('the response JSON path "{path}" should be >= {value:d}')
def step_assert_json_path_ge(context, path, value):
    """Verify numerical value is greater than or equal to X."""
    assert context.response_json is not None, "Response JSON is empty."
    actual = get_json_path(context.response_json, path)
    assert actual >= value, f"Expected >= {value}, got {actual}"

@then('the response JSON path "{path}" should be <= {value:d}')
def step_assert_json_path_le(context, path, value):
    """Verify numerical value is less than or equal to X."""
    assert context.response_json is not None, "Response JSON is empty."
    actual = get_json_path(context.response_json, path)
    assert actual <= value, f"Expected <= {value}, got {actual}"

@then('the response JSON path "{path}" should be > {value:d}')
def step_assert_json_path_gt(context, path, value):
    """Verify numerical value is strictly greater than X."""
    assert context.response_json is not None, "Response JSON is empty."
    actual = get_json_path(context.response_json, path)
    assert actual > value, f"Expected > {value}, got {actual}"

@then('the response JSON path "{path}" should be < {value:d}')
def step_assert_json_path_lt(context, path, value):
    """Verify numerical value is strictly less than X."""
    assert context.response_json is not None, "Response JSON is empty."
    actual = get_json_path(context.response_json, path)
    assert actual < value, f"Expected < {value}, got {actual}"

@then('the response JSON path "{path}" should be true')
def step_assert_json_path_true(context, path: str):
    """Verify boolean value is true."""
    assert context.response_json is not None, "Response JSON is empty."
    actual = get_json_path(context.response_json, path)
    assert actual is True or actual == "true" or actual == True, f"Expected true at '{path}', got {actual}"

@then('the response JSON path "{path}" should be false')
def step_assert_json_path_false(context, path: str):
    """Verify boolean value is false."""
    assert context.response_json is not None, "Response JSON is empty."
    actual = get_json_path(context.response_json, path)
    assert actual is False or actual == "false" or actual == False, f"Expected false at '{path}', got {actual}"

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 7: VARIABLES & DATA STORAGE
# ═══════════════════════════════════════════════════════════════════════════════

@then('I store the response JSON path "{path}" as "{var_name}"')
def step_store_response_json_path(context, path: str, var_name: str):
    """Extract a value from the response and store it in context.vars."""
    assert context.response_json is not None, "Response JSON is empty."
    value = get_json_path(context.response_json, path)
    if not hasattr(context, "vars") or context.vars is None: context.vars = {}
    context.vars[var_name] = value
    ContextualLogger.debug(f"Stored JSON value from '{path}' as '${{{var_name}}}': {value}", context)

@then('the response JSON path "{path}" should equal stored variable "{var_name}"')
def step_json_path_equals_stored_var(context, path: str, var_name: str):
    """Verify a JSON value matches a previously stored variable."""
    assert context.response_json is not None, "Response JSON is empty."
    vars = getattr(context, "vars", {})
    expected = vars.get(var_name)
    actual = get_json_path(context.response_json, path)
    assert actual == expected, f"Expected {expected}, got {actual}"

@then('the stored variables "{var_a}" and "{var_b}" should be different')
def step_stored_vars_should_be_different(context, var_a: str, var_b: str):
    """Verify two stored variables do not have the same value."""
    vars = getattr(context, "vars", {})
    a, b = vars.get(var_a), vars.get(var_b)
    assert a != b, f"Expected different values, both were '{a}'"

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 8: DEBUGGING & LOGGING
# ═══════════════════════════════════════════════════════════════════════════════

@then("I print the response JSON")
def step_print_response_json(context):
    """Pretty-print the response JSON for debugging."""
    assert context.response_json is not None, "Response JSON is empty."
    ContextualLogger.section("Response JSON")
    print(json.dumps(context.response_json, indent=2, ensure_ascii=False, sort_keys=True))
    print("═"*65)

@then(u'I print the request headers')
def step_print_request_headers(context):
    """Print the headers actually sent in the last request."""
    assert context.response is not None, "No response found."
    sent_headers = dict(context.response.request.headers)
    ContextualLogger.section("Request Headers (sent)")
    print(json.dumps(sent_headers, indent=2, ensure_ascii=False, sort_keys=True))
    print("═"*65)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 9: SECURITY SANITY CHECKS
# ═══════════════════════════════════════════════════════════════════════════════

@then("the response should not leak server metadata")
def step_security_no_metadata_leaks(context):
    """
    Verify that the response doesn't contain sensitive server technology headers.
    Checks for 'Server' and 'X-Powered-By' leakage.
    """
    assert context.response is not None, "No response found."
    headers = context.response.headers
    
    leaked = []
    # 1. Server header: Should be absent or generic (e.g. 'nginx' without version)
    server = headers.get("Server", "")
    if server and any(char.isdigit() for char in server):
        leaked.append(f"Server: {server}")
        
    # 2. X-Powered-By: Should be completely absent
    powered_by = headers.get("X-Powered-By")
    if powered_by:
        leaked.append(f"X-Powered-By: {powered_by}")
        
    if leaked:
        msg = f"Security Leak Detected: {', '.join(leaked)}"
        ContextualLogger.error(msg, context)
        raise AssertionError(msg)
    
    ContextualLogger.success("No server metadata leaks detected.", context)

@then("the response should contain mandatory security headers")
def step_security_mandatory_headers(context):
    """
    Verify the presence of essential security headers:
    - HSTS, X-Content-Type-Options, X-Frame-Options, CSP
    """
    assert context.response is not None, "No response found."
    headers = context.response.headers
    missing = []
    
    checks = {
        "Strict-Transport-Security": "HSTS missing (prevents MITM)",
        "X-Content-Type-Options": "MIME-sniffing protection missing",
        "X-Frame-Options": "Clickjacking protection missing",
        "Content-Security-Policy": "CSP missing (XSS protection)"
    }
    
    for header, description in checks.items():
        if header not in headers:
            missing.append(f"{header} ({description})")
            
    if missing:
        msg = f"Missing Security Headers: {'; '.join(missing)}"
        ContextualLogger.warning(msg, context)
        raise AssertionError(msg)

    ContextualLogger.success("All mandatory security headers are present.", context)

@then("all session cookies should be secure")
def step_security_cookies(context):
    """
    Verify that all cookies in the response have security flags:
    - Secure (HTTPS only)
    - HttpOnly (No JS access)
    - SameSite (CSRF protection)
    """
    assert context.response is not None, "No response found."
    cookies = context.response.cookies
    insecure = []
    
    for cookie in cookies:
        issues = []
        if not cookie.secure: issues.append("Missing 'Secure' flag")
        
        # Requests cookiejar handling for HttpOnly
        is_httponly = False
        if hasattr(cookie, 'has_nonstandard_attr') and cookie.has_nonstandard_attr('HttpOnly'):
            is_httponly = True
        elif 'httponly' in str(cookie).lower():
            is_httponly = True
        elif getattr(cookie, 'httponly', False):
            is_httponly = True
            
        if not is_httponly:
            issues.append("Missing 'HttpOnly' flag")
        
        # SameSite check
        samesite = getattr(cookie, 'rest', {}).get('SameSite', '').lower()
        if samesite not in ['strict', 'lax']:
            issues.append(f"Insecure SameSite: {samesite or 'None'}")
            
        if issues:
            insecure.append(f"Cookie '{cookie.name}': {', '.join(issues)}")
            
    if insecure:
        msg = f"Insecure Cookies Detected: {'; '.join(insecure)}"
        ContextualLogger.error(msg, context)
        raise AssertionError(msg)
        
    ContextualLogger.success("All response cookies are properly secured.", context)
