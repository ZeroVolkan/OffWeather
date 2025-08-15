from collections.abc import Callable
from typing import Union
import toml
import os

class Setting():
    def __init__(self, file_path):
        """Initialize settings by loading data from a TOML file."""
        self.file_path = file_path
        self.data = self.load()

    def load(self):
        """Load and return data from the TOML file."""
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as file:
                toml.dump({}, file)

        with open(self.file_path, 'r') as file:
            return toml.load(file)

    def save(self, obj, path: list[str]):
        """Save object data to a TOML path by extracting values from object's annotations."""
        # Создаем структуру по пути, если она не существует
        current = self.data
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        # Получаем данные из объекта
        obj_data = {}
        if hasattr(obj.__class__, "__annotations__"):
            for name, t in obj.__class__.__annotations__.items():
                if hasattr(obj, name):
                    value = getattr(obj, name)
                    # Сохраняем только не-None значения
                    if value is not None:
                        obj_data[name] = value
                else:
                    raise AttributeError(f"Object doesn't have attribute '{name}'")
        else:
            raise TypeError("Object's class doesn't have __annotations__")

        # Сохраняем данные по указанному пути
        if len(path) > 0:
            current[path[-1]] = obj_data
        else:
            self.data.update(obj_data)

        # Записываем в файл
        with open(self.file_path, 'w') as file:
            toml.dump(self.data, file)

    def fetch(self, obj: Callable, path: list[str]):
        """Fetch values from a TOML path and cast them to types from a class's annotations."""
        try:
            select = self.data
            for i in path:
                select = select[i]
        except KeyError:
            # Если путь не существует, возвращаем объект с дефолтными значениями
            return obj()

        kwargs = {}
        if "__annotations__" in obj.__dict__:
            for name, annotation in obj.__annotations__.items():
                if name in select:
                    value = select[name]
                    # Если значение None, оставляем его как None
                    if value is None:
                        kwargs[name] = None
                    else:
                        # Обрабатываем Union типы (например, str | None)
                        if hasattr(annotation, '__origin__') and annotation.__origin__ is Union:
                            # Для Union типов берем первый не-None тип
                            for arg in annotation.__args__:
                                if arg is not type(None):
                                    kwargs[name] = arg(value)
                                    break
                        elif hasattr(annotation, '__args__'):  # Для types.UnionType в Python 3.10+
                            # Берем первый не-None тип из Union
                            for arg in annotation.__args__:
                                if arg is not type(None):
                                    kwargs[name] = arg(value)
                                    break
                        else:
                            # Обычный тип
                            kwargs[name] = annotation(value)
                # Если ключа нет в данных, не добавляем его в kwargs (будет использовано значение по умолчанию)
        else:
            raise TypeError("Class don't have __annotation__")

        if hasattr(obj, "__init__") and obj.__init__ is not object.__init__:
            return obj(**kwargs)
        else:
            raise TypeError(f"{obj.__name__} doesn't have a usable __init__")

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
        with open(self.file_path, 'w') as file:
            toml.dump(self.data, file)

    def __str__(self):
        return f"Setting({self.file_path})"
