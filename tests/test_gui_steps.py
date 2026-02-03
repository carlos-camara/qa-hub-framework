import pytest
from unittest.mock import MagicMock, patch
from selenium.common.exceptions import TimeoutException
from qa_framework.steps.gui_steps import (
    step_navigate_to_url,
    step_verify_text_present,
    step_verify_page_title
)

def test_step_navigate():
    context = MagicMock()
    step_navigate_to_url(context, "http://test.com")
    context.driver.get.assert_called_with("http://test.com")

def test_step_verify_text_present_pass():
    context = MagicMock()
    context.driver.page_source = "Welcome User"
    step_verify_text_present(context, "Welcome")

def test_step_verify_text_present_fail():
    context = MagicMock()
    context.driver.page_source = "Error page"
    with pytest.raises(AssertionError, match="Text 'Welcome' not found"):
        step_verify_text_present(context, "Welcome")

@patch("qa_framework.steps.gui_steps.WebDriverWait")
def test_step_verify_title_pass(mock_wait):
    context = MagicMock()
    context.driver.title = "Home Page"
    # Mock the until method to return True
    mock_wait.return_value.until.return_value = True
    
    step_verify_page_title(context, "Home Page")
    mock_wait.return_value.until.assert_called()

@patch("qa_framework.steps.gui_steps.WebDriverWait")
def test_step_verify_title_fail(mock_wait):
    context = MagicMock()
    context.driver.title = "Login Page"
    
    # Mock until to raise TimeoutException
    mock_wait.return_value.until.side_effect = TimeoutException("Mock Timeout")
    
    with pytest.raises(TimeoutException, match="Mock Timeout"):
        step_verify_page_title(context, "Home Page")
