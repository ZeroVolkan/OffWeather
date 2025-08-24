from loguru import logger
import requests

from src.api import WeatherEndpoint
from src.errors import SettingsError, ResponseError


class ForecastEndpoint[OpenMeteoAPI](WeatherEndpoint):
    def __init__(
        self,
        api: OpenMeteoAPI,
        latitude: float | None = None,
        longitude: float | None = None,
    ):
        super().__init__(api)
        self.url = "https://api.open-meteo.com/v1/forecast"

        self.latitude = latitude
        self.longitude = longitude

    def refresh(self):
        session: requests.Session = self.api.session

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
            logger.error(f"{self.__class__.__name__} Error API: {response.status_code}")
            raise ResponseError(f"API error: {response.status_code}")

    def check(self, **kwargs):
        """Проверяет настройки Endpoint"""
        if self.latitude is None or self.longitude is None:
            logger.error("Сoordinates not specified")
            raise SettingsError("coordinates not specified")
