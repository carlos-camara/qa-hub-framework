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

@given('the API base URL is "{base_url}"')
def step_set_base_url(context, base_url: str):
    context.base_url = base_url
    context.response = None
    context.response_json = None
    context.last_request = None

@when('I send a "{method}" request to "{path}"')
def step_send_request_simple(context, method: str, path: str):
    context.vars = getattr(context, "vars", {}) or {}
    resolved_path = substitute_vars(path, context.vars) if "${" in path else path
    url = full_url(context.base_url, resolved_path)
    method_u = method.upper()
    context.last_request = {"method": method_u, "url": url, "params": None, "json": None}
    if not hasattr(context, "default_headers") or context.default_headers is None:
        context.default_headers = {}
    resp = requests.request(method=method_u, url=url, headers=context.default_headers, timeout=20)
    context.response = resp
    try:
        context.response_json = resp.json()
    except Exception:
        context.response_json = None

@when('I send a "{method}" request to "{path}" with query parameters')
def step_send_request_with_query(context, method: str, path: str):
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

@when("I set request headers")
def step_set_request_headers(context):
    if context.table is None:
        raise AssertionError("This step requires a table.")
    if not hasattr(context, "default_headers") or context.default_headers is None:
        context.default_headers = {}
    new_headers = table_to_params(context.table)
    context.default_headers.update(new_headers)

@when('I send a "POST" request to "{path}" with form data')
def step_post_with_form_data(context, path: str):
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
    """Generic multipart upload."""
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

@then("the response status code should be {status_code:d}")
def step_assert_status(context, status_code: int):
    assert context.response is not None, "No response found."
    actual = context.response.status_code
    assert actual == status_code, f"Expected {status_code}, got {actual}. Body: {context.response.text[:500]}"

@then('the response JSON path "{path}" should be "{expected}"')
def step_assert_json_path_str(context, path: str, expected: str):
    assert context.response_json is not None, "Response JSON is empty."
    actual = get_json_path(context.response_json, path)
    exp = parse_expected(expected)
    assert actual == exp, f"JSON mismatch at '{path}'. Expected: {exp}, Actual: {actual}"

@then('the response JSON path "{path}" should be {expected:d}')
def step_assert_json_path_int(context, path: str, expected: int):
    assert context.response_json is not None, "Response JSON is empty."
    actual = get_json_path(context.response_json, path)
    assert actual == expected, f"JSON mismatch at '{path}'. Expected: {expected}, Actual: {actual}"

@then('the response JSON path "{path}" should be a "{py_type}"')
def step_assert_json_type(context, path: str, py_type: str):
    assert context.response_json is not None, "Response JSON is empty."
    val = get_json_path(context.response_json, path)
    mapping = {"str": str, "int": int, "float": float, "bool": bool, "dict": dict, "list": list}
    if py_type not in mapping: raise AssertionError(f"Unsupported type '{py_type}'.")
    assert isinstance(val, mapping[py_type]), f"Expected {py_type}, got {type(val)}"

@then('the response JSON path "{path}" should contain "{substring}"')
def step_assert_json_path_contains(context, path: str, substring: str):
    assert context.response_json is not None, "Response JSON is empty."
    actual = get_json_path(context.response_json, path)
    assert substring in str(actual), f"Expected '{substring}' to be in '{actual}'"

@then('the response JSON path "{path}" should be >= {value:d}')
def step_assert_json_path_ge(context, path, value):
    assert context.response_json is not None, "Response JSON is empty."
    actual = get_json_path(context.response_json, path)
    assert actual >= value, f"Expected >= {value}, got {actual}"

@then('the response JSON path "{path}" should be null')
def step_json_path_should_be_null(context, path: str):
    assert context.response_json is not None, "Response JSON is empty."
    val = get_json_path(context.response_json, path)
    assert val is None, f"Expected null, got {val}"

@then('the response header "{header_name}" should be "{expected}"')
def step_assert_response_header(context, header_name: str, expected: str):
    assert context.response is not None, "No response found."
    headers = context.response_json.get("headers", {}) if context.response_json and isinstance(context.response_json, dict) else context.response.headers
    actual = get_header_case_insensitive(headers, header_name)
    assert actual == expected, f"Expected {expected}, got {actual}"

@then('the response JSON path "{path}" should match regex "{pattern}"')
def step_json_path_matches_regex(context, path: str, pattern: str):
    assert context.response_json is not None, "Response JSON is empty."
    val = get_json_path(context.response_json, path)
    assert re.match(pattern, str(val)), f"Value '{val}' did not match regex '{pattern}'"

@then("the response body should be empty")
def step_response_body_empty(context):
    assert context.response is not None, "No response found."
    assert context.response.text.strip() == "", "Expected empty body."

@then("the response time should be less than {ms:d} ms")
def step_assert_time(context, ms: int):
    assert context.response is not None, "No response found."
    elapsed_ms = context.response.elapsed.total_seconds() * 1000.0
    assert elapsed_ms < ms, f"Response time too high: {elapsed_ms:.2f} ms (limit: {ms} ms)"

@then('I store the response JSON path "{path}" as "{var_name}"')
def step_store_response_json_path(context, path: str, var_name: str):
    assert context.response_json is not None, "Response JSON is empty."
    value = get_json_path(context.response_json, path)
    if not hasattr(context, "vars") or context.vars is None: context.vars = {}
    context.vars[var_name] = value

@then('the stored variables "{var_a}" and "{var_b}" should be different')
def step_stored_vars_should_be_different(context, var_a: str, var_b: str):
    vars = getattr(context, "vars", {})
    a, b = vars.get(var_a), vars.get(var_b)
    assert a != b, f"Expected different values, both were '{a}'"

@then('the response JSON path "{path}" should equal stored variable "{var_name}"')
def step_json_path_equals_stored_var(context, path: str, var_name: str):
    assert context.response_json is not None, "Response JSON is empty."
    vars = getattr(context, "vars", {})
    expected = vars.get(var_name)
    actual = get_json_path(context.response_json, path)
    assert actual == expected, f"Expected {expected}, got {actual}"

@then("I print the response JSON")
def step_print_response_json(context):
    assert context.response_json is not None, "Response JSON is empty."
    print("\n===== RESPONSE JSON =====\n" + json.dumps(context.response_json, indent=2, ensure_ascii=False, sort_keys=True) + "\n=========================\n")

@then(u'I print the request headers')
def step_print_request_headers(context):
    assert context.response is not None, "No response found."
    sent_headers = dict(context.response.request.headers)
    print("\n===== REQUEST HEADERS (sent) =====\n" + json.dumps(sent_headers, indent=2, ensure_ascii=False, sort_keys=True) + "\n==================================\n")

@then('the response header "{header_name}" should contain "{expected}"')
def step_assert_response_header_contains(context, header_name: str, expected: str):
    assert context.response is not None, "No response found."
    headers = context.response.headers
    actual = get_header_case_insensitive(headers, header_name)
    assert expected in actual, f"Expected '{expected}' to be in '{actual}'"

@then('the response JSON should not be empty')
def step_assert_json_not_empty(context):
    assert context.response_json is not None, "Response JSON is None."
    if isinstance(context.response_json, dict):
        assert len(context.response_json) > 0, "Response JSON is an empty dictionary."
    elif isinstance(context.response_json, list):
        assert len(context.response_json) > 0, "Response JSON is an empty list."
    else:
        # If it's a scalar, just check it's not None (already asserted above)
        pass

@then('the response JSON should contain keys')
def step_assert_json_contains_keys(context):
    assert context.response_json is not None, "Response JSON is None."
    assert isinstance(context.response_json, dict), "Response JSON is not a dictionary."
    if context.table:
        for row in context.table:
            key = row[0]
            assert key in context.response_json, f"Key '{key}' not found in response JSON."

@then('the response JSON path "{path}" should be true')
def step_assert_json_path_true(context, path: str):
    assert context.response_json is not None, "Response JSON is empty."
    actual = get_json_path(context.response_json, path)
    assert actual is True or actual == "true" or actual == True, f"Expected true at '{path}', got {actual}"

@then('the response JSON path "{path}" should be false')
def step_assert_json_path_false(context, path: str):
    assert context.response_json is not None, "Response JSON is empty."
    actual = get_json_path(context.response_json, path)
    assert actual is False or actual == "false" or actual == False, f"Expected false at '{path}', got {actual}"
