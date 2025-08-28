from typing import Callable
import toml
import os

from .errors import ConfigError
from .utils import safe_cast, unwrap_union_type


class Setting:
    def __init__(self, file_path):
        """Initialize settings by loading data from a TOML file."""
        self.file_path = file_path
        self.data = self.load()

    def load(self):
        """Load and return data from the TOML file."""
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as file:
                toml.dump({}, file)

        with open(self.file_path, "r") as file:
            return toml.load(file)

    def save(self, obj, path: list[str]):
        """Save object data to a TOML path by extracting values from object's annotations."""
        # Create structure by path if it doesn't exist
        current = self.data
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        # Get object data
        obj_data = {}
        if hasattr(obj.__class__, "__annotations__"):
            for name, t in obj.__class__.__annotations__.items():
                if hasattr(obj, name):
                    value = getattr(obj, name)
                    # Save only non-None values
                    if value is not None:
                        obj_data[name] = value
                else:
                    raise ConfigError(f"Object doesn't have attribute '{name}'")
        else:
            raise ConfigError("Object's class doesn't have __annotations__")

        # Save data on path
        if len(path) > 0:
            current[path[-1]] = obj_data
        else:
            self.data.update(obj_data)

        # Write to file
        with open(self.file_path, "w") as file:
            toml.dump(self.data, file)

    def _cast_value(self, value, annotation):
        """Cast value to type annotation (considering Union and None)."""
        if value is None:
            return None

        try:
            # Try to unwrap union type and cast
            target_type = unwrap_union_type(annotation)
            return safe_cast(target_type, value)
        except (ValueError, TypeError):
            # If unwrapping fails, try direct casting
            try:
                return annotation(value)
            except (ValueError, TypeError):
                return value

    def fetch(self, obj: Callable, path: list[str]):
        """Fetch values from a TOML path and cast them to types from a class's annotations."""
        try:
            select = self.data
            for i in path:
                select = select[i]
        except KeyError:
            return obj()

        if not hasattr(obj, "__annotations__"):
            raise ConfigError("Class doesn't have __annotations__")

        kwargs = {}
        for name, annotation in obj.__annotations__.items():
            if name in select:
                kwargs[name] = self._cast_value(select[name], annotation)

        if hasattr(obj, "__init__") and obj.__init__ is not object.__init__:
            return obj(**kwargs)
        raise ConfigError(f"{obj.__name__} doesn't have a usable __init__")

    def add(self, key, value):
        """Add a new key-value pair to settings and save."""
        self.data[key] = value
        self._save_file()

    def update(self, data: dict):
        """Update settings with a dictionary and save."""
        self.data.update(data)
        self._save_file()

    def _save_file(self):
        """Internal method to save current data to the TOML file."""
        with open(self.file_path, "w") as file:
            toml.dump(self.data, file)

    def __str__(self):
        return f"Setting({self.file_path})"
