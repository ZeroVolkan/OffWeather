import requests
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
        self.api = api
        # Check
        if self.api.id is None and self.api.city is None:
            raise ConfigError("Please set at least one setting: id, city")

    def run(self, **kwargs):
        try:
            geo = self.api.get("GeoEndpoint")
        except EndpointError:
            self.api.add("GeoEndpoint")
            geo = self.api.get("GeoEndpoint")

        geo.refresh()
        result = self.api.data.get("GeoList")

        if result is None:
            logger.error("GeoList not found")
            raise DataError("GeoList not found")
        else:
            ln = len(result.results)
            if ln == 0:
                logger.error("Information not found")
                raise ResponseError("Information not found")
            elif ln == 1:
                self.api.data["GeoList"] = result[0]
            else:
                logger.info("Multiple Geo found, need to select")

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
