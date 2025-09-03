from typing import Union, get_args, get_origin
from types import NoneType, UnionType
from typing_extensions import Any

from pydantic import BaseModel

import inspect

class classproperty:
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        return self.func(owner)


def unwrap_union_type[T](union_type: type[T] | UnionType) -> T:
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


def unwrap_and_cast[T](target_type: type[T], value) -> T:
    """Cast value to target_type. Supports Union[T, None], containers (list, tuple, dict) and Pydantic models."""

    if value is None:
        raise ValueError("Cannot unwrap None value")

    origin = get_origin(target_type)
    if origin is Union:
        args = [arg for arg in get_args(target_type) if arg is not type(None)]
        if len(args) == 1:
            target_type = args[0]
            origin = get_origin(target_type)
        else:
            raise ValueError(f"Union {target_type} слишком сложный")

    # ---- Контейнеры ----
    if origin is list:
        (elem_type,) = get_args(target_type)
        return [unwrap_and_cast(elem_type, v) for v in value]  # type: ignore

    if origin is tuple:
        elem_types = get_args(target_type)
        if len(elem_types) == len(value):
            return tuple(unwrap_and_cast(t, v) for t, v in zip(elem_types, value))  # type: ignore
        else:
            raise ValueError(f"Tuple размер не совпадает: {value}")

    if origin is dict:
        key_type, val_type = get_args(target_type)
        return {
            unwrap_and_cast(key_type, k): unwrap_and_cast(val_type, v)
            for k, v in value.items()
        }  # type: ignore

    # ---- Pydantic модели ----
    if inspect.isclass(target_type) and issubclass(target_type, BaseModel):
        fields = list(target_type.model_fields.keys())

        if isinstance(value, dict):
            return target_type(**value)  # type: ignore

        if isinstance(value, (list, tuple)):
            if len(value) != len(fields):
                raise ValueError(
                    f"{target_type.__name__} ожидает {len(fields)} полей, получено {len(value)}"
                )
            casted = {
                f: unwrap_and_cast(target_type.model_fields[f].annotation, v)  # type: ignore
                for f, v in zip(fields, value)
            }
            return target_type(**casted)  # type: ignore

        raise ValueError(f"Cannot cast {type(value)} to {target_type}")

    # ---- Простой тип ----
    try:
        return target_type(value)  # type: ignore
    except Exception as e:
        raise ValueError(f"Cannot cast {value!r} to {target_type}: {e}")


# def unwrap_and_cast[T](target_type: type[T], value) -> T:
#     """Cast value to target_type. Supports Union[T, None] types. Raises ValueError if value is None."""
#     if value is None:
#         raise ValueError("Cannot unwrap None value")

#     # Handle Union types (both typing.Union and | syntax)
#     origin = type(value)

#     if origin is Union:
#         args = list(filter(lambda x: x is not None, get_args(origin)))

#         if len(args) == 1:
#             origin = args[0]
#         else:
#             raise ValueError(f"Cannot cast {value} to {target_type}")

#     if isinstance(origin, Callable):
#         return target_type(value)  # pyright: ignore[reportCallIssue]
#     raise ValueError(f"Cannot cast {value} to {target_type}")


def safe_cast[T](target_type: type[T], value: Any, default: Any = None) -> T | None:
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
