"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           QA Hub Framework                                    ║
║                        HTTP Utilities Unit Tests                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Tests for HTTP utility functions including:                                 ║
║  • JSON path navigation      • Variable substitution                         ║
║  • Type parsing              • URL construction                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import pytest
from qa_framework.utils.http import get_json_path, substitute_vars, parse_expected, full_url


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1: JSON PATH NAVIGATION
# ═══════════════════════════════════════════════════════════════════════════════

class TestJsonPath:
    """Tests for the get_json_path utility function."""

    def test_simple_key(self):
        """✓ Extracts value from simple key."""
        payload = {"name": "Carlos", "age": 30}
        assert get_json_path(payload, "name") == "Carlos"

    def test_nested_dict(self):
        """✓ Navigates nested dictionary structures."""
        payload = {"user": {"profile": {"name": "Carlos"}}}
        assert get_json_path(payload, "user.profile.name") == "Carlos"

    def test_deeply_nested(self):
        """✓ Handles deeply nested structures."""
        payload = {"a": {"b": {"c": {"d": {"e": 42}}}}}
        assert get_json_path(payload, "a.b.c.d.e") == 42

    def test_array_index(self):
        """✓ Accesses array elements by index."""
        payload = [{"id": 10}, {"id": 20}, {"id": 30}]
        assert get_json_path(payload, "1.id") == 20

    def test_nested_array(self):
        """✓ Navigates mixed dict/array structures."""
        payload = {"users": [{"name": "Alice"}, {"name": "Bob"}]}
        assert get_json_path(payload, "users.0.name") == "Alice"

    def test_missing_key_raises_error(self):
        """✓ Raises AssertionError for missing keys."""
        payload = {"a": 1}
        with pytest.raises(AssertionError, match="JSON path not found"):
            get_json_path(payload, "b")

    def test_missing_nested_key(self):
        """✓ Raises AssertionError for missing nested keys."""
        payload = {"a": {"b": 1}}
        with pytest.raises(AssertionError, match="JSON path not found"):
            get_json_path(payload, "a.c")

    def test_out_of_range_index(self):
        """✓ Raises AssertionError for out-of-range array index."""
        payload = [1, 2, 3]
        with pytest.raises(AssertionError, match="index out of range"):
            get_json_path(payload, "5")

    def test_numeric_value(self):
        """✓ Returns numeric values correctly."""
        payload = {"count": 123, "price": 99.99}
        assert get_json_path(payload, "count") == 123
        assert get_json_path(payload, "price") == 99.99

    def test_boolean_value(self):
        """✓ Returns boolean values correctly."""
        payload = {"active": True, "deleted": False}
        assert get_json_path(payload, "active") is True
        assert get_json_path(payload, "deleted") is False

    def test_null_value(self):
        """✓ Returns None for null values."""
        payload = {"optional": None}
        assert get_json_path(payload, "optional") is None


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2: VARIABLE SUBSTITUTION
# ═══════════════════════════════════════════════════════════════════════════════

class TestVariableSubstitution:
    """Tests for the substitute_vars utility function."""

    def test_single_variable(self):
        """✓ Substitutes a single variable."""
        vars = {"id": 123}
        raw = "Item ID: ${id}"
        assert substitute_vars(raw, vars) == "Item ID: 123"

    def test_multiple_variables(self):
        """✓ Substitutes multiple variables in one string."""
        vars = {"name": "Carlos", "role": "admin"}
        raw = "User ${name} is ${role}"
        assert substitute_vars(raw, vars) == "User Carlos is admin"

    def test_repeated_variable(self):
        """✓ Substitutes the same variable multiple times."""
        vars = {"id": 42}
        raw = "ID: ${id}, Confirm: ${id}"
        assert substitute_vars(raw, vars) == "ID: 42, Confirm: 42"

    def test_missing_variable_raises_error(self):
        """✓ Raises AssertionError for undefined variables."""
        vars = {"name": "test"}
        with pytest.raises(AssertionError, match="Variable 'id' not found"):
            substitute_vars("User ${id}", vars)

    def test_empty_vars(self):
        """✓ Works with empty vars dict when no substitution needed."""
        vars = {}
        raw = "No variables here"
        assert substitute_vars(raw, vars) == "No variables here"

    def test_string_value(self):
        """✓ Substitutes string values correctly."""
        vars = {"email": "test@example.com"}
        raw = "Contact: ${email}"
        assert substitute_vars(raw, vars) == "Contact: test@example.com"

    def test_numeric_value_to_string(self):
        """✓ Converts numeric values to strings."""
        vars = {"count": 42}
        raw = "Count: ${count}"
        result = substitute_vars(raw, vars)
        assert "42" in result


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3: TYPE PARSING
# ═══════════════════════════════════════════════════════════════════════════════

class TestTypeParsing:
    """Tests for the parse_expected utility function."""

    def test_parse_integer(self):
        """✓ Parses integer strings to int."""
        assert parse_expected("123") == 123
        assert parse_expected("-456") == -456
        assert parse_expected("0") == 0

    def test_parse_float(self):
        """✓ Parses float strings to float."""
        assert parse_expected("3.14") == 3.14
        assert parse_expected("-2.5") == -2.5

    def test_parse_boolean_true(self):
        """✓ Parses 'true' (JSON literal) to True."""
        # Note: json.loads only parses lowercase true/false
        assert parse_expected("true") is True

    def test_parse_boolean_false(self):
        """✓ Parses 'false' (JSON literal) to False."""
        assert parse_expected("false") is False

    def test_parse_null(self):
        """✓ Parses 'null' (JSON literal) to None."""
        assert parse_expected("null") is None

    def test_parse_plain_string(self):
        """✓ Returns plain strings unchanged."""
        assert parse_expected("hello world") == "hello world"
        assert parse_expected("test123") == "test123"

    def test_parse_json_object(self):
        """✓ Parses JSON object strings."""
        result = parse_expected('{"key": "value"}')
        assert result == {"key": "value"}

    def test_parse_json_array(self):
        """✓ Parses JSON array strings."""
        result = parse_expected('[1, 2, 3]')
        assert result == [1, 2, 3]

    def test_parse_empty_string(self):
        """✓ Returns empty string for empty input."""
        assert parse_expected("") == ""

    def test_parse_capitalized_returns_string(self):
        """✓ Capitalized True/False are not JSON, returned as strings."""
        # json.loads requires lowercase, so these remain strings
        assert parse_expected("True") == "True"
        assert parse_expected("False") == "False"
        assert parse_expected("None") == "None"


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4: URL CONSTRUCTION
# ═══════════════════════════════════════════════════════════════════════════════

class TestUrlConstruction:
    """Tests for the full_url utility function."""

    def test_base_with_leading_slash_path(self):
        """✓ Joins base URL with path starting with /."""
        result = full_url("http://api.com", "/users")
        assert result == "http://api.com/users"

    def test_base_with_trailing_slash(self):
        """✓ Handles base URL with trailing slash."""
        result = full_url("http://api.com/", "users")
        assert result == "http://api.com/users"

    def test_base_without_slash_path_without_slash(self):
        """✓ Adds slash between base and path."""
        result = full_url("http://api.com", "users")
        assert result == "http://api.com/users"

    def test_both_have_slashes(self):
        """✓ Handles double slashes correctly."""
        result = full_url("http://api.com/", "/users")
        assert result == "http://api.com/users"

    def test_complex_path(self):
        """✓ Handles complex paths with multiple segments."""
        result = full_url("http://api.com", "/v1/users/123")
        assert result == "http://api.com/v1/users/123"

    def test_with_port(self):
        """✓ Works with URLs containing ports."""
        result = full_url("http://localhost:3000", "/api/data")
        assert result == "http://localhost:3000/api/data"

    def test_https(self):
        """✓ Works with HTTPS URLs."""
        result = full_url("https://secure.api.com", "/auth/token")
        assert result == "https://secure.api.com/auth/token"

    def test_empty_path(self):
        """✓ Handles empty path (adds trailing slash)."""
        result = full_url("http://api.com", "")
        # Current implementation: base.rstrip("/") + "/" + "".lstrip("/") = "http://api.com/"
        assert result == "http://api.com/"


# ═══════════════════════════════════════════════════════════════════════════════
# RUN CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
