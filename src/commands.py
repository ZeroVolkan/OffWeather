from .api import WeatherAPI, CommandAPI
from .errors import SettingError
from loguru import logger


class Up(CommandAPI):
    def __init__(self, api: WeatherAPI) -> None:
        self.name: str = self.__class__.__name__
        self.api: WeatherAPI = api

    def execute(self, name: str | None = None):
        if name is None:
            logger.error("Don't set name")
            raise SettingError("Don't set name")

        self.api.add(name)
        logger.info(f"{self.name} added")


class Refresh(CommandAPI):
    def __init__(self, api: WeatherAPI) -> None:
        self.name: str = self.__class__.__name__
        self.api: WeatherAPI = api

    def execute(self, name: str | None = None):
        if name is None:
            logger.error("Don't set name")
            raise SettingError("Don't set name")

        geo = self.api.get(name)
        geo.refresh()
        logger.info(f"{geo.name} refreshed")


class Down(CommandAPI):
    def __init__(self, api: WeatherAPI) -> None:
        self.name: str = self.__class__.__name__
        self.api: WeatherAPI = api

    def execute(self, name: str | None = None):
        if name is None:
            logger.error("Don't set name")
            raise SettingError("Don't set name")

        self.api.delete(name)
        logger.info(f"Deleted {name}")
