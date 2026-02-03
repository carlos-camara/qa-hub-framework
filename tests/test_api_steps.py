import pytest
from unittest.mock import MagicMock
from qa_framework.steps.api_steps import (
    step_assert_status, 
    step_store_response_json_path,
    step_assert_json_path_str
)

def test_step_assert_status_pass():
    context = MagicMock()
    context.response.status_code = 200
    step_assert_status(context, 200)

def test_step_assert_status_fail():
    context = MagicMock()
    context.response.status_code = 404
    context.response.text = "Not Found"
    with pytest.raises(AssertionError, match="Expected 200, got 404"):
        step_assert_status(context, 200)

def test_step_store_response_json_path():
    context = MagicMock()
    context.response_json = {"id": "12345"}
    context.vars = {}
    
    step_store_response_json_path(context, "id", "my_id")
    
    assert context.vars["my_id"] == "12345"

def test_step_assert_json_path_str_pass():
    context = MagicMock()
    context.response_json = {"user": {"name": "Carlos"}}
    step_assert_json_path_str(context, "user.name", "Carlos")

def test_step_assert_json_path_str_fail():
    context = MagicMock()
    context.response_json = {"user": {"name": "Carlos"}}
    with pytest.raises(AssertionError, match="JSON mismatch"):
        step_assert_json_path_str(context, "user.name", "Jose")
