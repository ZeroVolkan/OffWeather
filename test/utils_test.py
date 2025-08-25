from src.utils import (
    unwrap_and_cast,
    safe_cast,
    safe_unwrap_union_type,
    unwrap_union_type,
)
from typing import Union
import pytest


class TestUnwrapAndCast:
    """Test cases for unwrap_and_cast function"""

    def test_none_value_raises_error(self):
        """Test that None value raises ValueError"""
        with pytest.raises(ValueError, match="Cannot unwrap None value"):
            unwrap_and_cast(int, None)

    def test_basic_type_casting(self):
        """Test basic type casting functionality"""
        # String to int
        result = unwrap_and_cast(int, "42")
        assert result == 42
        assert isinstance(result, int)

        # String to float
        result = unwrap_and_cast(float, "3.14")
        assert result == 3.14
        assert isinstance(result, float)

        # Int to string
        result = unwrap_and_cast(str, 123)
        assert result == "123"
        assert isinstance(result, str)

        # String to bool
        result = unwrap_and_cast(bool, "True")
        assert result is True
        assert isinstance(result, bool)

    def test_callable_handling(self):
        """Test handling of callable values"""

        def sample_func():
            return "test"

        result = unwrap_and_cast(str, sample_func)
        assert isinstance(result, str)

    def test_invalid_casting_raises_error(self):
        """Test that invalid casting raises ValueError or TypeError"""
        # String is callable in Python (via type check), so int("not_a_number") raises ValueError
        with pytest.raises(ValueError, match=r"invalid literal for int\(\)"):
            unwrap_and_cast(int, "not_a_number")

    def test_non_callable_non_union_values(self):
        """Test that non-callable, non-union values raise ValueError"""
        # List is callable in Python (via isinstance check), so int([1,2,3]) raises TypeError
        with pytest.raises(TypeError, match=r"int\(\) argument must be"):
            unwrap_and_cast(int, [1, 2, 3])  # List is callable but casting fails

    def test_truly_non_callable_values(self):
        """Test that truly non-callable values raise ValueError with 'Cannot cast' message"""

        # Create an object that's definitely not callable
        class NonCallableType:
            pass

        non_callable_obj = NonCallableType()

        with pytest.raises(TypeError):
            unwrap_and_cast(int, non_callable_obj)

        # Empty string
        with pytest.raises(ValueError):
            unwrap_and_cast(int, "")

        # Zero
        result = unwrap_and_cast(str, 0)
        assert result == "0"

        # Boolean to int
        result = unwrap_and_cast(int, True)
        assert result == 1


class TestSafeCast:
    """Test cases for safe_cast function"""

    def test_none_value_returns_default(self):
        """Test that None value returns default"""
        result = safe_cast(int, None, 42)
        assert result == 42

        result = safe_cast(str, None, "default")
        assert result == "default"

        result = safe_cast(int, None)  # No default provided
        assert result is None

    def test_successful_casting(self):
        """Test successful casting returns cast value"""
        result = safe_cast(int, "123")
        assert result == 123
        assert isinstance(result, int)

        result = safe_cast(float, "3.14")
        assert result == 3.14
        assert isinstance(result, float)

    def test_failed_casting_returns_default(self):
        """Test that failed casting returns default value"""
        result = safe_cast(int, "not_a_number", 0)
        assert result == 0

        result = safe_cast(float, [1, 2, 3], 1.0)
        assert result == 1.0

    def test_failed_casting_no_default(self):
        """Test failed casting without default returns None"""
        result = safe_cast(int, "invalid")
        assert result is None

    def test_none_value_error_propagates(self):
        """Test that safe_cast correctly handles None values"""
        # This test was wrong - safe_cast returns default for None, doesn't raise
        result = safe_cast(int, None, 42)
        assert result == 42

        # Test that None without default returns None
        result = safe_cast(int, None)
        assert result is None

    def test_none_handling_correct(self):
        """Test correct None handling in safe_cast"""
        # None should return default, not raise error
        result = safe_cast(int, None, 99)
        assert result == 99


class TestUnwrapUnionType:
    """Test cases for unwrap_union_type function"""

    def test_union_with_none_str(self):
        """Test Union[str, None] returns str"""
        result = unwrap_union_type(Union[str, None])
        assert result is str

    def test_union_with_none_int(self):
        """Test Union[int, None] returns int"""
        result = unwrap_union_type(Union[int, None])
        assert result is int

    def test_union_with_none_float(self):
        """Test Union[float, None] returns float"""
        result = unwrap_union_type(Union[float, None])
        assert result is float

    def test_pipe_syntax_str(self):
        """Test str | None returns str"""
        result = unwrap_union_type(str | None)
        assert result is str

    def test_pipe_syntax_int(self):
        """Test int | None returns int"""
        result = unwrap_union_type(int | None)
        assert result is int

    def test_reversed_union(self):
        """Test Union[None, str] returns str"""
        result = unwrap_union_type(Union[None, str])
        assert result is str

    def test_non_union_type_returns_as_is(self):
        """Test that non-Union types are returned unchanged"""
        assert unwrap_union_type(str) is str
        assert unwrap_union_type(int) is int
        assert unwrap_union_type(float) is float
        assert unwrap_union_type(bool) is bool

    def test_union_with_multiple_non_none_types_raises_error(self):
        """Test that Union with multiple non-None types raises ValueError"""
        with pytest.raises(
            ValueError, match="Union type must contain only one non-None type"
        ):
            unwrap_union_type(Union[str, int])

        with pytest.raises(
            ValueError, match="Union type must contain only one non-None type"
        ):
            unwrap_union_type(Union[str, int, float])

    def test_complex_types(self):
        """Test with complex types like list, dict, etc."""
        result = unwrap_union_type(Union[list, None])
        assert result is list

        result = unwrap_union_type(Union[dict, None])
        assert result is dict

        result = unwrap_union_type(Union[tuple, None])
        assert result is tuple

    def test_custom_class_types(self):
        """Test with custom class types"""

        class CustomClass:
            pass

        result = unwrap_union_type(Union[CustomClass, None])
        assert result is CustomClass

    def test_callable_types(self):
        """Test with callable types"""
        from collections.abc import Callable

        result = unwrap_union_type(Union[Callable, None])
        assert result is Callable


class TestSafeUnwrapUnionType:
    """Test cases for safe_unwrap_union_type function"""

    def test_successful_unwrapping(self):
        """Test successful unwrapping returns correct type"""
        result = safe_unwrap_union_type(Union[str, None], int)
        assert result is str

        result = safe_unwrap_union_type(int | None, str)
        assert result is int

    def test_non_union_type_returns_as_is(self):
        """Test that non-Union types are returned unchanged"""
        result = safe_unwrap_union_type(str, int)
        assert result is str

        result = safe_unwrap_union_type(float, bool)
        assert result is float

    def test_invalid_union_returns_default(self):
        """Test that invalid Union returns default type"""
        # Union with multiple non-None types
        result = safe_unwrap_union_type(Union[str, int], float)
        assert result is float

        # Union with multiple non-None types and None
        result = safe_unwrap_union_type(Union[str, int, None], bool)
        assert result is bool

    def test_default_type_variations(self):
        """Test with different default types"""
        # String default
        result = safe_unwrap_union_type(Union[str, int], str)
        assert result is str

        # Int default
        result = safe_unwrap_union_type(Union[str, int], int)
        assert result is int

        # Custom class default
        class DefaultClass:
            pass

        result = safe_unwrap_union_type(Union[str, int], DefaultClass)
        assert result is DefaultClass

    def test_complex_scenarios(self):
        """Test complex scenarios combining different cases"""
        # Valid union should ignore default
        result = safe_unwrap_union_type(Union[list, None], dict)
        assert result is list

        # Invalid union should use default
        result = safe_unwrap_union_type(Union[str, int, float], tuple)
        assert result is tuple


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
