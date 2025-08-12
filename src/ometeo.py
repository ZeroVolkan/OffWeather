import requests
from requests_cache import CachedSession
from retry_requests import retry

from loguru import logger

from api import WeatherAPI
from endpoins.forecast import ForecastEndpoint
from endpoins.geo import GeoEndpoint


class OpenMeteoAPI(WeatherAPI):
    def __init__(
        self,
        id: int | None = None,
        city: str | None = None,
        language: str | None = None,
        country: str | None = None,
        count: int | None = None,
    ):
        super().__init__()

        self.session: requests.Session = retry(
            CachedSession(".cache/", expire_after=3600), retries=5, backoff_factor=0.2
        )

        try:
            self.add_endpoint(
                GeoEndpoint(
                    self,
                    id=id,
                    city=city,
                    language=language,
                    country=country,
                    count=count,
                )
            )

            # self.add_endpoint(ForecastEndpoint(self, latitude=0., longitude=0.))
        except Exception as e:
            logger.error(f"Error settings API: {e}")
            raise ValueError("Error settings API")

    def setting(self, resetup: bool = False, **kwargs):
        """Меняет настройки API"""
        for key, value in kwargs.items():
            self.__dict__[key] = value
        if resetup:
            self.__init__(**self.__dict__)

    def check(self, **kwargs):
        """Проверяет настройки API"""
        pass
