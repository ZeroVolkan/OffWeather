import requests
from requests_cache import CachedSession
from retry_requests import retry

from loguru import logger

from src.api import WeatherAPI
from src.errors import SettingsError, UnknownApiError
from src.models import Coordinates
from .forecast import ForecastEndpoint
from .geo import GeoEndpoint


class OpenMeteoAPI(WeatherAPI):
    def __init__(
        self,
        id: int | None = None,
        city: str | None = None,
        language: str | None = None,
        country: str | None = None,
        count: int | None = None,
        coordinates: Coordinates | None = None,
        **kwargs
    ):
        super().__init__()

        self.id = id
        self.city = city
        self.language = language
        self.country = country
        self.count = count
        self.coordinates = coordinates

        self.session: requests.Session = retry(
            CachedSession(".cache/", expire_after=3600), retries=5, backoff_factor=0.2
        )

    def up(self):
        self.check()

        try:
            self.add_endpoint(
                GeoEndpoint(
                self,
                id=self.id,
                city=self.city,
                language=self.language,
                country=self.country,
                count=self.count,
                )
            )
            self.add_endpoint(ForecastEndpoint(self))
        except Exception as e:
            logger.error(f"Unknown API error: {e}")
            raise UnknownApiError("Unknown API error")

    def setting(self, resetup: bool = False, **kwargs):
        """Меняет настройки API"""
        for key, value in kwargs.items():
            self.__dict__[key] = value
        if resetup:
            self.__init__(**self.__dict__)

    def check(self, **kwargs):
        """Проверяет настройки API"""
        if self.id is None and self.city is None and self.coordinates is None:
            raise SettingsError("Please set at least one setting: id, city, or coordinates")
