import importlib

# API dictionary for easy editing
apis = {
    "open_meteo": {
        "module": "src.open_meteo.api",
        "class": "OpenMeteoAPI",
        "config": "OpenMeteoConfig",
    },
    # Add new APIs here
}


class Information:
    """Singleton for lazy loading of APIs and their configurations."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_loaded_apis"):
            self._loaded_apis = {}

    def __getattr__(self, api_key):
        if api_key not in apis:
            raise AttributeError(f"API {api_key} not found")

        if api_key in self._loaded_apis:
            return self._loaded_apis[api_key]

        api_info = apis[api_key]
        try:
            module = importlib.import_module(api_info["module"])
            api_class = getattr(module, api_info["class"])
            config_class = getattr(module, api_info["config"])
            result = {"class": api_class, "config": config_class}
            self._loaded_apis[api_key] = result
            return result
        except (ImportError, AttributeError) as e:
            raise RuntimeError(f"Error loading API {api_key}: {e}")

    @property
    def available(self) -> dict:
        """Get all available API (key -> description)."""
        return apis

    def get(self, api_name: str) -> dict:
        """Безопасно получить API-инфо."""
        if api_name not in apis:
            raise AttributeError(f"API {api_name} not found")
        return getattr(self, api_name)
