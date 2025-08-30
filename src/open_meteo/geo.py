from pydantic import BaseModel
from loguru import logger
import requests

from src.api import WeatherEndpoint
from src.errors import ResponseError, SettingError


class DataGeoEndpoint(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    elevation: float
    feature_code: str
    country_code: str
    admin1_id: int
    admin2_id: int
    admin3_id: int
    admin4_id: int
    timezone: str
    population: int
    postcodes: list[str]
    country_id: int
    country: str
    admin1: str
    admin2: str
    admin3: str
    admin4: str


class DataGeoEndpointList(BaseModel):
    results: list[DataGeoEndpoint]


class GeoEndpoint(WeatherEndpoint):
    def __init__(
        self,
        api,
    ):
        super().__init__(api)  # create attr name, api, data
        self.url = "https://geocoding-api.open-meteo.com/v1/search"

        self.id = self.api.id
        self.city = self.api.city
        self.language = self.api.language
        self.country = self.api.country
        self.count = self.api.count

        self.check()

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

        self.data["DataGeoEndpoint"] = DataGeoEndpointList(**response_data["results"])

    def check(self):
        """Check settings of Endpoint"""
        if self.id is None and self.city is None:
            logger.error("id or city not specified")
            raise SettingError("id or city not specified")
