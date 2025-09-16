from .api import WeatherAPI, CommandAPI
from src.errors import SettingError
from loguru import logger


class Add(CommandAPI):
    """Add new endpoint to API"""

    def __init__(self, api: WeatherAPI) -> None:
        self.api: WeatherAPI = api

    def execute(self, name: str | None = None):
        if name is None:
            logger.error("Don't set name")
            raise SettingError("Don't set name")

        self.api.add(name)
        logger.info(f"{name} added")


class Refresh(CommandAPI):
    """Refresh endpoint from API"""

    def __init__(self, api: WeatherAPI) -> None:
        self.api: WeatherAPI = api

    def execute(self, name: str | None = None):
        if name is None:
            logger.error("Don't set name")
            raise SettingError("Don't set name")

        end = self.api.get(name)
        end.refresh()
        logger.info(f"{end.name} refreshed")


class Delete(CommandAPI):
    """Delete endpoint from API"""

    def __init__(self, api: WeatherAPI) -> None:
        self.api: WeatherAPI = api

    def execute(self, name: str | None = None):
        if name is None:
            logger.error("Don't set name")
            raise SettingError("Don't set name")

        self.api.delete(name)
        logger.info(f"Deleted {name}")


class Data(CommandAPI):
    """Data endpoint from API"""

    def __init__(self, api: WeatherAPI) -> None:
        self.api: WeatherAPI = api

    def execute(self, name: str | None = None):
        if name is None:
            logger.error("Don't set name")
            raise SettingError("Don't set name")

        end = self.api.get(name)
        logger.info(f"{end.name} data: {end.data}")
