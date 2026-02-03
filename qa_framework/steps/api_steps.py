from behave import given, when, then
import requests
import re
import json
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

@then("the response time should be less than {ms:d} ms")
def step_assert_time(context, ms: int):
    assert context.response is not None, "No response found."
    elapsed_ms = context.response.elapsed.total_seconds() * 1000.0
    assert elapsed_ms < ms, f"Response time too high: {elapsed_ms:.2f} ms (limit: {ms} ms)"

@then('I store the response JSON path "{path}" as "{var_name}"')
def step_store_response_json_path(context, path: str, var_name: str):
    assert context.response_json is not None, "Response JSON is empty."
    value = get_json_path(context.response_json, path)
    if not hasattr(context, "vars") or context.vars is None:
        context.vars = {}
    context.vars[var_name] = value
