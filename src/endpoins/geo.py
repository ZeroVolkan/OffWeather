from api import WeatherEndpoint
from loguru import logger

import requests

class GeoEndpoint(WeatherEndpoint):
    def setup(self, **kwargs):
        self.url = "https://geocoding-api.open-meteo.com/v1/search"

        self.id = kwargs.get("id", None)
        self.city = kwargs.get("city", None)
        self.language = kwargs.get("language", "en")
        self.country = kwargs.get("country", None)
        self.count = kwargs.get("count", 10)


    def refresh(self, forced: bool = False):
        session: requests.Session = self.api.session

        params = {
            "name": self.city,
            "language": self.language,
            "country": self.country,
            "count": self.count
        }

        responce = session.get(self.url, params=params)

        if responce.status_code != 200:
            logger.error(f"Ошибка при получении данных: {responce.status_code}")

        response_data = responce.json()

        if self.id is None:
            self.data = response_data["results"]
        else:
            for result in response_data["results"]:
                if self.id == result["id"]:
                   self.data = result
                   break


    def check(self, **kwargs):
        """Проверяет настройки Endpoint"""
        if not self.id and not self.city:
            logger.error("Не указаны id или город")
            raise ValueError("Не указаны id или город")

    def select_id(self, id: int | None = None):
        self.id = id
