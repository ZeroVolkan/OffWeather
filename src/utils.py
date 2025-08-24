from typing import Union, get_args, get_origin, Callable
from types import NoneType, UnionType
from typing_extensions import Any

def unwrap_union_type[T: type](union_type: T | UnionType) -> T:
    """Extract non-None type from Union[T, None] or T | None. Returns the actual type T."""
    origin = get_origin(union_type)


    if origin is Union:
        args = get_args(union_type)
        non_none_types = [arg for arg in args if arg is not NoneType]
        if not non_none_types or len(non_none_types) != 1:
            raise ValueError("Union type must contain only one non-None type")
        return non_none_types[0]

    if isinstance(union_type, UnionType):
        args = union_type.__args__
        non_none_types = [arg for arg in args if arg is not NoneType]
        if not non_none_types or len(non_none_types) != 1:
            raise ValueError("Union type must contain only one non-None type")
        return non_none_types[0]

    return union_type


def safe_unwrap_union_type(union_type: type | UnionType, default_type: type) -> type:
    """Safely extract non-None type from Union, returns default_type if extraction fails."""
    try:
        result = unwrap_union_type(union_type)
        return result
    except (ValueError, TypeError):
        return default_type


def unwrap_and_cast[T: type](target_type: T, value) -> T:
    """Cast value to target_type. Supports Union[T, None] types. Raises ValueError if value is None."""
    if value is None:
        raise ValueError("Cannot unwrap None value")

    # Handle Union types (both typing.Union and | syntax)
    origin = type(value)

    if origin is Union:
        args = list(filter(lambda x: x is not None, get_args(origin)))

        if len(args) == 1:
            origin = args[0]
        else:
            raise ValueError(f"Cannot cast {value} to {target_type}")

    if isinstance(origin, Callable):
        return target_type(value)
    raise ValueError(f"Cannot cast {value} to {target_type}")


def safe_cast[T: type](target_type: T, value: Any, default: Any = None) -> T | None:
    """Safely cast value to target_type, returns default if value is None."""
    if value is None:
        return default

    try:
        return unwrap_and_cast(target_type, value)
    except (ValueError, TypeError) as e:
        # Re-raise ValueError (None value), catch only casting errors
        if "Cannot unwrap None value" in str(e):
            raise
        return default
