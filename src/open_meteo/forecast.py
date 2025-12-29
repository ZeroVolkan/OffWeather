from loguru import logger
from typing import cast
import requests

from src.core.api import BaseEndpoint
from src.errors import SettingError, ResponseError
from src.open_meteo.api import OpenMeteoAPI


class ForecastEndpoint(BaseEndpoint):
    def __init__(self, api):
        self.meteo: OpenMeteoAPI = cast(OpenMeteoAPI, api)
        self.url = "https://api.open-meteo.com/v1/forecast"
        self.check()
        self.latitude, self.longitude = self.meteo.coordinates

    def refresh(self):
        session: requests.Session = self.meteo.session

        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timeformat": "unixtime",
            "current": [
                "weather_code",
                "temperature_2m",
                "apparent_temperature",
                "relative_humidity_2m",
                "wind_speed_10m",
                "wind_direction_10m",
                "wind_gusts_10m",
            ],
            "daily": [
                "weather_code",
                "temperature_2m_min",
                "temperature_2m_max",
                "temperature_2m_mean",
                "apparent_temperature_min",
                "apparent_temperature_max",
                "apparent_temperature_mean",
                "relative_humidity_2m_min",
                "relative_humidity_2m_max",
                "relative_humidity_2m_mean",
                "wind_speed_10m_min",
                "wind_speed_10m_max",
                "wind_speed_10m_mean",
                "wind_gusts_10m_min",
                "wind_gusts_10m_max",
                "wind_gusts_10m_mean",
                "wind_direction_10m_dominant",
            ],
        }

        response = session.get(self.url, params=params)

        if response.status_code == 200:
            json_data = response.json()
            current = json_data.get("current", {})
            daily = json_data.get("daily", {})
            self.data = {"current": current, "daily": daily}

        else:
            logger.error(
                f"{self.name} Error network request failed: {response.status_code}"
            )
            raise ResponseError(f"Network request failed: {response.status_code}")

    def check(self):
        """Check settings of Endpoint"""
        if self.meteo.coordinates is None:
            logger.error("Coordinates not specified")
            raise SettingError("Coordinates not specified")
