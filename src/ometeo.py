import requests
from requests_cache import CachedSession
from retry_requests import retry

from loguru import logger

from api import WeatherAPI
from endpoins.forecast import ForecastEndpoint
from endpoins.geo import GeoEndpoint

class OpenMeteoAPI(WeatherAPI):
    def setup(self, config, **kwargs):
        self.config = config
        self.kwargs = kwargs

        self.session: requests.Session = retry(
            CachedSession(".cache/", expire_after = 3600),
            retries = 5, backoff_factor = 0.2
        )

        try:
            self.add_endpoint(GeoEndpoint(self))

            self.endpoints["GeoEndpoint"].data["city"]


            self.add_endpoint(ForecastEndpoint(self))
        except Exception as e:
            logger.error(f"Ошибка при проверке настроек API: {e}")
            raise ValueError("Ошибка при проверке настроек API") # Temporaly

    def setting(self, resetup: bool = False, **kwargs):
        """Меняет настройки API"""
        for key, value in kwargs.items():
            self.kwargs[key] = value
        if resetup:
            self.setup(self.config, **self.kwargs)

    def check(self, **kwargs):
        """Проверяет настройки API"""
        if not self.config:
            logger.error("Не указаны настройки API")
            raise ValueError("Не указаны или не верные настройки API")


# TEMPORALY TESTING
if __name__ == "__main__":
    from main import init_loguru
    init_loguru()
    api = OpenMeteoAPI("None")
    api.refresh()
