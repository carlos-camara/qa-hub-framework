import pytest
from qa_framework.utils.http import get_json_path, substitute_vars, parse_expected, full_url

def test_get_json_path_dict():
    payload = {"a": {"b": 1}}
    assert get_json_path(payload, "a.b") == 1

def test_get_json_path_list():
    payload = [{"id": 10}, {"id": 20}]
    assert get_json_path(payload, "1.id") == 20

def test_get_json_path_error():
    payload = {"a": 1}
    with pytest.raises(AssertionError, match="JSON path not found"):
        get_json_path(payload, "b")

def test_substitute_vars_success():
    vars = {"id": 123, "name": "test"}
    raw = "User ${name} has id ${id}"
    assert substitute_vars(raw, vars) == "User test has id 123"

def test_substitute_vars_missing():
    vars = {"name": "test"}
    with pytest.raises(AssertionError, match="Variable 'id' not found"):
        substitute_vars("User ${id}", vars)

def test_parse_expected_types():
    assert parse_expected("123") == 123
    assert parse_expected("true") is True
    assert parse_expected("false") is False
    assert parse_expected("null") is None
    assert parse_expected("plain string") == "plain string"
    assert parse_expected('{"key": "val"}') == {"key": "val"}

def test_full_url():
    assert full_url("http://api.com", "/path") == "http://api.com/path"
    assert full_url("http://api.com/", "path") == "http://api.com/path"
    assert full_url("http://api.com", "path") == "http://api.com/path"
