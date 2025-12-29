from loguru import logger
from typing import cast

import requests

from src.core.api import BaseEndpoint
from src.errors import ResponseError, SettingError
from .api import OpenMeteoAPI
from .schemas import GeoList, Geo


class GeoEndpoint(BaseEndpoint):
    def __init__(
        self,
        api,
    ):
        self.api: OpenMeteoAPI = cast(OpenMeteoAPI, api)
        self.data = {}

        self.url = "https://geocoding-api.open-meteo.com/v1/search"

        self.id = self.api.id
        self.city = self.api.city
        self.language = self.api.language
        self.country = self.api.country
        self.count = self.api.count

        self.check()

    def refresh(self):
        session: requests.Session = self.api.session

        params = {
            "name": self.city,
            "language": self.language,
            "country": self.country,
            "count": self.count,
        }

        response: requests.Response = session.get(self.url, params=params)

        if response.status_code != 200:
            logger.error(f"Error network request failed: {response.status_code}")
            raise ResponseError(f"Error network request failed: {response.status_code}")

        self.api.data["GeoList"] = GeoList(**response.json())

    def check(self):
        """Check settings of Endpoint"""
        if self.id is None and self.city is None:
            logger.error("id or city not specified")
            raise SettingError("id or city not specified")
