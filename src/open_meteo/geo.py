from loguru import logger
import requests

from src.api import WeatherEndpoint
from src.errors import ResponseError, SettingError


class GeoEndpoint[OpenMeteoAPI](WeatherEndpoint):
    def __init__(
        self,
        api: OpenMeteoAPI,
        id: int | None = None,
        city: str | None = None,
        language: str | None = None,
        country: str | None = None,
        count: int | None = None,
    ):
        self.url = "https://geocoding-api.open-meteo.com/v1/search"

        self.id = id
        self.city = city
        self.language = language
        self.country = country
        self.count = count

        super().__init__(api)

    def refresh(self, forced: bool = False):
        session: requests.Session = self.api.session

        params = {
            "name": self.city,
            "language": self.language,
            "country": self.country,
            "count": self.count,
        }

        response = session.get(self.url, params=params)

        if response.status_code != 200:
            logger.error(f"Error network request failed: {response.status_code}")
            raise ResponseError(f"Error network request failed: {response.status_code}")

        response_data = response.json()

        if self.id is None:
            self.data = response_data["results"]
        else:
            for result in response_data["results"]:
                if self.id == result["id"]:
                    self.data = result
                    break

    def check(self):
        """Check settings of Endpoint"""
        if self.id is None and self.city is None:
            logger.error("id or city not specified")
            raise SettingError("id or city not specified")

    def select_id(self, id: int | None = None):
        self.id = id
