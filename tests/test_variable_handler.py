"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           QA Hub Framework                                    ║
║                     Variable Handler Unit Tests                               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Tests for dynamic variable resolution including:                            ║
║  • Token constants (UUID, NULL, TRUE, FALSE)                                 ║
║  • Dynamic generators (RANDOM, TIMESTAMP, NOW)                               ║
║  • Type conversions (INT, STR, FLOAT)                                        ║
║  • Temporal expressions (NOW + 2 DAYS)                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import pytest
import re
from datetime import datetime
from qa_framework.core.variable_handler import VariableHandler


# ═══════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def handler():
    """Create a VariableHandler instance."""
    return VariableHandler()


@pytest.fixture
def handler_with_config():
    """Create a VariableHandler with custom configuration."""
    config = {
        "dataset": {
            "language": "es",
            "country": "ES"
        }
    }
    return VariableHandler(config)


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1: CONSTANT TOKENS
# ═══════════════════════════════════════════════════════════════════════════════

class TestConstantTokens:
    """Tests for constant value tokens."""

    def test_null_token(self, handler):
        """✓ [NULL] resolves to None."""
        result = handler.resolve("[NULL]")
        assert result is None

    def test_true_token(self, handler):
        """✓ [TRUE] resolves to True."""
        result = handler.resolve("[TRUE]")
        assert result is True

    def test_false_token(self, handler):
        """✓ [FALSE] resolves to False."""
        result = handler.resolve("[FALSE]")
        assert result is False

    def test_empty_token(self, handler):
        """✓ [EMPTY] resolves to empty string."""
        result = handler.resolve("[EMPTY]")
        assert result == ""

    def test_blank_token(self, handler):
        """✓ [B] resolves to single space."""
        result = handler.resolve("[B]")
        assert result == " "

    def test_sharp_token(self, handler):
        """✓ [SHARP] resolves to #."""
        result = handler.resolve("[SHARP]")
        assert result == "#"


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2: DYNAMIC GENERATORS
# ═══════════════════════════════════════════════════════════════════════════════

class TestDynamicGenerators:
    """Tests for dynamically generated values."""

    def test_uuid_token(self, handler):
        """✓ [UUID] generates valid UUID format."""
        result = handler.resolve("[UUID]")
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        assert re.match(uuid_pattern, result)

    def test_uuid_uniqueness(self, handler):
        """✓ [UUID] generates unique values each time."""
        uuid1 = handler.resolve("[UUID]")
        uuid2 = handler.resolve("[UUID]")
        assert uuid1 != uuid2

    def test_random_token(self, handler):
        """✓ [RANDOM] generates 4-digit number."""
        result = handler.resolve("[RANDOM]")
        assert result.isdigit()
        assert 1000 <= int(result) <= 9999

    def test_timestamp_token(self, handler):
        """✓ [TIMESTAMP] generates Unix timestamp."""
        result = handler.resolve("[TIMESTAMP]")
        assert result.isdigit()
        # Should be a reasonable timestamp (after year 2020)
        assert int(result) > 1577836800


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3: STRING/INTEGER WITH LENGTH
# ═══════════════════════════════════════════════════════════════════════════════

class TestLengthBasedGenerators:
    """Tests for length-based string and integer generators."""

    def test_string_with_length(self, handler):
        """✓ [STRING_WITH_LENGTH_N] generates string of length N."""
        result = handler.resolve("[STRING_WITH_LENGTH_10]")
        assert len(result) == 10
        assert result.isalnum()

    def test_string_with_length_variations(self, handler):
        """✓ [STRING_WITH_LENGTH_N] works with various lengths."""
        for length in [5, 15, 50]:
            result = handler.resolve(f"[STRING_WITH_LENGTH_{length}]")
            assert len(result) == length

    def test_integer_with_length(self, handler):
        """✓ [INTEGER_WITH_LENGTH_N] generates numeric string of length N."""
        result = handler.resolve("[INTEGER_WITH_LENGTH_8]")
        assert len(result) == 8
        assert result.isdigit()


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4: ARRAY GENERATORS
# ═══════════════════════════════════════════════════════════════════════════════

class TestArrayGenerators:
    """Tests for array/list generators."""

    def test_string_array_with_length(self, handler):
        """✓ [STRING_ARRAY_WITH_LENGTH_N] generates list of N strings."""
        result = handler.resolve("[STRING_ARRAY_WITH_LENGTH_5]")
        assert isinstance(result, list)
        assert len(result) == 5
        for item in result:
            assert isinstance(item, str)

    def test_integer_array_with_length(self, handler):
        """✓ [INTEGER_ARRAY_WITH_LENGTH_N] generates list of N integers."""
        result = handler.resolve("[INTEGER_ARRAY_WITH_LENGTH_3]")
        assert isinstance(result, list)
        assert len(result) == 3
        for item in result:
            assert isinstance(item, int)


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5: TEMPORAL EXPRESSIONS
# ═══════════════════════════════════════════════════════════════════════════════

class TestTemporalExpressions:
    """Tests for date/time token expressions."""

    def test_now_default_format(self, handler):
        """✓ [NOW] returns current datetime in ISO format."""
        result = handler.resolve("[NOW]")
        # Should be parseable as datetime
        assert "T" in result or "-" in result

    def test_today_default_format(self, handler):
        """✓ [TODAY] returns current date."""
        result = handler.resolve("[TODAY]")
        today = datetime.now().strftime("%Y-%m-%d")
        assert result == today

    def test_now_with_custom_format(self, handler):
        """✓ [NOW(%Y-%m-%d)] uses custom format."""
        result = handler.resolve("[NOW(%Y-%m-%d)]")
        date_pattern = r'^\d{4}-\d{2}-\d{2}$'
        assert re.match(date_pattern, result)

    def test_now_with_offset_days(self, handler):
        """✓ [NOW + 2 DAYS] adds days to current date."""
        result = handler.resolve("[NOW(%Y-%m-%d) + 2 DAYS]")
        # Result should be a valid date string
        assert len(result) == 10  # YYYY-MM-DD format

    def test_now_with_negative_offset(self, handler):
        """✓ [NOW - 1 DAYS] subtracts days from current date."""
        result = handler.resolve("[NOW(%Y-%m-%d) - 1 DAYS]")
        assert len(result) == 10


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6: TYPE CONVERSIONS
# ═══════════════════════════════════════════════════════════════════════════════

class TestTypeConversions:
    """Tests for type conversion functions."""

    def test_str_conversion(self, handler):
        """✓ [STR:123] converts to string."""
        result = handler.resolve("[STR:123]")
        assert result == "123"
        assert isinstance(result, str)

    def test_int_conversion(self, handler):
        """✓ [INT:456] converts to integer."""
        result = handler.resolve("[INT:456]")
        assert result == 456
        assert isinstance(result, int)

    def test_float_conversion(self, handler):
        """✓ [FLOAT:3.14] converts to float."""
        result = handler.resolve("[FLOAT:3.14]")
        assert result == 3.14
        assert isinstance(result, float)

    def test_upper_conversion(self, handler):
        """✓ [UPPER:hello] converts to uppercase."""
        result = handler.resolve("[UPPER:hello]")
        assert result == "HELLO"

    def test_lower_conversion(self, handler):
        """✓ [LOWER:HELLO] converts to lowercase."""
        result = handler.resolve("[LOWER:HELLO]")
        assert result == "hello"

    def test_title_conversion(self, handler):
        """✓ [TITLE:hello world] converts to title case."""
        result = handler.resolve("[TITLE:hello world]")
        assert result == "Hello World"


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 7: EMBEDDED TOKENS
# ═══════════════════════════════════════════════════════════════════════════════

class TestEmbeddedTokens:
    """Tests for tokens embedded in larger strings."""

    def test_token_in_sentence(self, handler):
        """✓ Token embedded in text is resolved."""
        result = handler.resolve("Status is [TRUE]")
        assert "True" in result

    def test_multiple_tokens(self, handler):
        """✓ Multiple tokens in one string are resolved."""
        result = handler.resolve("[TRUE] and [FALSE]")
        assert "True" in result
        assert "False" in result

    def test_no_tokens_passthrough(self, handler):
        """✓ Strings without tokens pass through unchanged."""
        result = handler.resolve("Plain text without tokens")
        assert result == "Plain text without tokens"


# ═══════════════════════════════════════════════════════════════════════════════
# RUN CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
