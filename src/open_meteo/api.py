import requests
from requests_cache import CachedSession
from retry_requests import retry
from dataclasses import dataclass
from loguru import logger

from src.core.api import WeatherAPI, ConfigAPI
from src.errors import SettingError, ApiError
from src.models import Coordinates


@dataclass
class OpenMeteoConfig(ConfigAPI):
    id: int | None = None
    api_key: str | None = None
    coordinates: Coordinates | None = None
    country: str | None = None
    city: str | None = None
    language: str | None = None
    count: int | None = None


class OpenMeteoAPI(WeatherAPI):
    def __init__(
        self,
        config: OpenMeteoConfig,
    ):
        super().__init__(config)

        self.id = config.id
        self.api_key = config.api_key
        self.coordinates = config.coordinates
        self.country = config.country
        self.city = config.city
        self.language = config.language
        self.count = config.count

        self.session: requests.Session = retry(
            CachedSession(".cache/", expire_after=3600), retries=5, backoff_factor=0.2
        )

    def up(self):
        self.check()

        try:
            pass
        except Exception as e:
            logger.error(f"Unknown API error: {e}")
            raise ApiError("Unknown API error")

    def check(self):
        """Check API settings"""
        if self.id is None and self.city is None and self.coordinates is None:
            raise SettingError(
                "Please set at least one setting: id, city, or coordinates"
            )
