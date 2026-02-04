"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           QA Hub Framework                                    ║
║                         API Steps Unit Tests                                  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Tests for API step definitions including:                                   ║
║  • Status code assertions    • JSON path extraction                          ║
║  • Variable storage          • List & Object assertions                      ║
║  • Boolean & Comparison ops  • Path existence checks                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import pytest
from unittest.mock import MagicMock, patch

# ═══════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def mock_context():
    """Create a mock Behave context with API response attributes."""
    context = MagicMock()
    context.response = MagicMock()
    context.response_json = {}
    context.vars = {}
    return context

@pytest.fixture
def sample_json():
    """Detailed sample JSON for complex path testing."""
    return {
        "id": 123,
        "active": True,
        "deleted": False,
        "meta": None,
        "items": [
            {"name": "A", "val": 10},
            {"name": "B", "val": 20},
            {"name": "C", "val": 30}
        ],
        "config": {
            "retries": 3,
            "mode": "production"
        },
        "tags": ["testing", "unit", "api"]
    }

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1: EXISTENCE & PREDICATES
# ═══════════════════════════════════════════════════════════════════════════════

class TestApiPredicates:
    """Tests for path existence and type predicates."""

    def test_path_exists_success(self, mock_context, sample_json):
        """✓ Verify 'path exists' works for deep paths."""
        from qa_framework.steps.api_steps import step_json_path_exists
        mock_context.response_json = sample_json
        step_json_path_exists(mock_context, "config.mode")
        step_json_path_exists(mock_context, "items.1.name")

    def test_path_exists_fails(self, mock_context, sample_json):
        """✓ Verify 'path exists' fails when path is missing."""
        from qa_framework.steps.api_steps import step_json_path_exists
        mock_context.response_json = sample_json
        with pytest.raises(AssertionError, match="does not exist"):
            step_json_path_exists(mock_context, "config.timeout")

    def test_path_not_exists_success(self, mock_context, sample_json):
        """✓ Verify 'path not exists' works."""
        from qa_framework.steps.api_steps import step_json_path_not_exists
        mock_context.response_json = sample_json
        step_json_path_not_exists(mock_context, "non_existent")

    def test_path_not_exists_fails(self, mock_context, sample_json):
        """✓ Verify 'path not exists' fails if path is actually found."""
        from qa_framework.steps.api_steps import step_json_path_not_exists
        mock_context.response_json = sample_json
        with pytest.raises(AssertionError, match="was found but should not exist"):
            step_json_path_not_exists(mock_context, "id")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2: LIST & OBJECT COUNT ASSERTIONS
# ═══════════════════════════════════════════════════════════════════════════════

class TestCollectionAssertions:
    """Tests for size and type of JSON collections."""

    def test_root_element_count(self, mock_context):
        """✓ Verify element count on root list."""
        from qa_framework.steps.api_steps import step_assert_json_count
        mock_context.response_json = [1, 2, 3, 4]
        step_assert_json_count(mock_context, 4)

    def test_path_element_count(self, mock_context, sample_json):
        """✓ Verify element count at specific path."""
        from qa_framework.steps.api_steps import step_assert_json_path_count
        mock_context.response_json = sample_json
        step_assert_json_path_count(mock_context, "items", 3)
        step_assert_json_path_count(mock_context, "tags", 3)

    def test_json_is_array(self, mock_context):
        """✓ Verify JSON type is array."""
        from qa_framework.steps.api_steps import step_assert_json_is_array
        mock_context.response_json = ["a", "b"]
        step_assert_json_is_array(mock_context)

    def test_json_is_object(self, mock_context, sample_json):
        """✓ Verify JSON type is object."""
        from qa_framework.steps.api_steps import step_assert_json_is_object
        mock_context.response_json = sample_json
        step_assert_json_is_object(mock_context)

    def test_json_is_object_fails(self, mock_context):
        """✓ Verify JSON type check fails on wrong type."""
        from qa_framework.steps.api_steps import step_assert_json_is_object
        mock_context.response_json = [1, 2] # List
        with pytest.raises(AssertionError, match="Expected object"):
            step_assert_json_is_object(mock_context)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3: BOOLEAN & MATHEMATICAL COMPARISONS
# ═══════════════════════════════════════════════════════════════════════════════

class TestValueComparisons:
    """Tests for boolean and numerical comparisons."""

    def test_boolean_assertions(self, mock_context, sample_json):
        """✓ Verify true/false assertions."""
        from qa_framework.steps.api_steps import (
            step_assert_json_path_true,
            step_assert_json_path_false
        )
        mock_context.response_json = sample_json
        step_assert_json_path_true(mock_context, "active")
        step_assert_json_path_false(mock_context, "deleted")

    def test_boolean_assertion_fails(self, mock_context, sample_json):
        """✓ Verify boolean assertions fail correctly."""
        from qa_framework.steps.api_steps import step_assert_json_path_true
        mock_context.response_json = sample_json
        with pytest.raises(AssertionError, match="Expected true"):
            step_assert_json_path_true(mock_context, "deleted")

    def test_math_operators(self, mock_context, sample_json):
        """✓ Verify mathematical operator steps (ge, le, gt, lt)."""
        from qa_framework.steps.api_steps import (
            step_assert_json_path_ge,
            step_assert_json_path_le,
            step_assert_json_path_gt,
            step_assert_json_path_lt
        )
        mock_context.response_json = sample_json
        
        # Path: id=123
        step_assert_json_path_ge(mock_context, "id", 123)
        step_assert_json_path_le(mock_context, "id", 123)
        step_assert_json_path_gt(mock_context, "id", 100)
        step_assert_json_path_lt(mock_context, "id", 200)

    def test_math_operator_fails(self, mock_context, sample_json):
        """✓ Verify math operations fail on mismatch."""
        from qa_framework.steps.api_steps import step_assert_json_path_gt
        mock_context.response_json = sample_json
        with pytest.raises(AssertionError, match="Expected > 200"):
            step_assert_json_path_gt(mock_context, "id", 200)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4: LEGACY & STATUS CORE TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestStatusAndCore:
    """Basic tests for status and storage to ensure no regressions."""

    def test_assert_status_code(self, mock_context):
        from qa_framework.steps.api_steps import step_assert_status
        mock_context.response.status_code = 200
        step_assert_status(mock_context, 200)

    def test_store_and_match_variable(self, mock_context, sample_json):
        from qa_framework.steps.api_steps import (
            step_store_response_json_path,
            step_json_path_equals_stored_var
        )
        mock_context.response_json = sample_json
        mock_context.vars = {}
        
        step_store_response_json_path(mock_context, "config.mode", "curr_mode")
        assert mock_context.vars["curr_mode"] == "production"
        
        step_json_path_equals_stored_var(mock_context, "config.mode", "curr_mode")

    def test_body_is_empty(self, mock_context):
        from qa_framework.steps.api_steps import step_response_body_empty
        mock_context.response.text = "   "
        step_response_body_empty(mock_context)

# ═══════════════════════════════════════════════════════════════════════════════
# RUN CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
