import requests
from typing import cast
from requests_cache import CachedSession
from retry_requests import retry
from dataclasses import dataclass
from loguru import logger

from src.core.api import ConfigAPI, BaseState, BaseAPI
from src.errors import EndpointError, ConfigError, ResponseError, DataError
from src.schemas import Coordinates

from .schemas import GeoList


@dataclass
class OpenMeteoConfig(ConfigAPI):
    id: int | None = None
    api_key: str | None = None
    coordinates: Coordinates | None = None
    country: str | None = None
    city: str | None = None
    language: str | None = None
    count: int | None = None


class OpenMeteoAPI(BaseAPI):
    def __init__(
        self,
        config: OpenMeteoConfig,
    ):
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

        if self.coordinates:
            super().__init__(config, MainState, {})
        elif self.city or self.id:
            super().__init__(config, ClarificationState, {})
            logger.info("Please set at least one setting: id, city or coordinates")
        else:
            raise ConfigError(
                "Please set at least one setting: id, city or coordinates"
            )


class ClarificationState(BaseState):
    def __init__(self, api: OpenMeteoAPI):
        self.api: OpenMeteoAPI = api
        # Check
        if self.api.id is None and self.api.city is None:
            raise ConfigError("Please set at least one setting: id, city")

    def run(self, **kwargs):
        id = int(k) if (k := kwargs.get("id")) else None

        try:
            geo = self.api.get("GeoEndpoint")
        except EndpointError:
            self.api.add("GeoEndpoint")
            geo = self.api.get("GeoEndpoint")

        geo.refresh()
        geo_list_raw = self.api.data.get('GeoList')

        if geo_list_raw and isinstance(geo_list_raw, GeoList):
            geo_list: GeoList = geo_list_raw
            ln = len(geo_list.results)

            if ln == 0:
                logger.error("Information not found")
                raise ResponseError("Information not found")
            elif ln == 1:
                self.api.data["GeoList"] = geo_list.results[0]
            elif id and id in map(lambda i: i.id, self.api.data["GeoList"].results):
                for i in geo_list.results:
                    if i.id == id:
                        self.api.coordinates = Coordinates(latitude=i.latitude, longitude=i.longitude)
                        self.api.to(MainState)
                        break
            else:
                logger.info("Multiple Geo found, need to select")
        else:
            logger.error("GeoList not found")
            raise DataError("GeoList not found")

    def to(self, state: BaseState) -> None:
        self.api._state = state

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.api})"


class MainState(BaseState):
    def __init__(self, api: OpenMeteoAPI):
        self.api = api

    def run(self, **kwargs):
        pass

    def to(self, state: BaseState) -> None:
        self.api._state = state

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.api})"
