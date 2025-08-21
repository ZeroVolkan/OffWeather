from api import WeatherEndpoint
from loguru import logger

import requests

from errors import ResponseError, SettingsError


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

        responce = session.get(self.url, params=params)

        if responce.status_code != 200:
            logger.error(f"Ошибка при получении данных: {responce.status_code}")
            raise ResponseError(f"Ошибка при получении данных: {responce.status_code}")

        response_data = responce.json()

        if self.id is None:
            self.data = response_data["results"]
        else:
            for result in response_data["results"]:
                if self.id == result["id"]:
                    self.data = result
                    break

    def check(self):
        """Проверяет настройки Endpoint"""
        if self.id is None and self.city is None:
            logger.error("id or city not specified")
            raise SettingsError("id or city not specified")

    def select_id(self, id: int | None = None):
        self.id = id
