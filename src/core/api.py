from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import final, Any, Type
from loguru import logger


from src.errors import EndpointError, APIError
from src.static import apis
from src.utils import classproperty


@dataclass
class ConfigAPI(ABC):
    pass


class StateAPI(ABC):
    capable: list[Type[StateAPI]] = []

    @abstractmethod
    def __init__(self, api: WeatherAPI):
        self.api = api

    @final
    def to(self, to: StateAPI):
        """Change state"""
        if type(to) not in self.capable:
            raise APIError(f"Can't change state from {self.__class__.__name__} to {to.__class__.__name__}")

        to.check()
        self.api._state = to

    @abstractmethod
    def check(self):
        """Check safe of transaction"""
        pass


class WeatherEndpoint(ABC):
    @classproperty
    def name(cls) -> str:
        return cls.__name__

    @abstractmethod
    def __init__(self, api):
        self.api = api
        self.data: dict[str, Any] = {}
        logger.info(f"Initialized endpoint {self.name} with attributes {self.__dict__}")

    @abstractmethod
    def refresh(self):
        """Update data for variables that store weather data"""
        pass

    @abstractmethod
    def check(self):
        """Check Endpoint"""
        pass


class WeatherAPI(ABC):
    @classproperty
    def name(cls) -> str:
        return cls.__name__

    @abstractmethod
    def __init__(self, config: ConfigAPI, init_state: type[StateAPI] = StateAPI):
        self.config = config
        self.apis = apis()
        self._state = init_state(self)
        self._endpoints: dict[str, WeatherEndpoint] = {}

    @abstractmethod
    def check(self):
        """Check API settings"""
        pass

    @abstractmethod
    def to(self, state: type[StateAPI]):
        self._state.to(state(self))

    def _to_name_and_instance(self, endpoint: str | type[WeatherEndpoint]) -> tuple[str, WeatherEndpoint]:
        if isinstance(endpoint, type) and issubclass(endpoint, WeatherEndpoint):
            return endpoint.name, endpoint(self)
        if isinstance(endpoint, str):
            return endpoint, self.apis[self.name]["endpoints"][endpoint](self)
        raise TypeError(f"Invalid endpoint type: {type(endpoint)}")

    def _to_name(self, endpoint: str | type[WeatherEndpoint]) -> str:
        if isinstance(endpoint, type) and issubclass(endpoint, WeatherEndpoint):
            return endpoint.name
        if isinstance(endpoint, str):
            return endpoint
        raise TypeError(f"Invalid endpoint type: {type(endpoint)}")

    @final
    def add(self, endpoint: str | type[WeatherEndpoint]):
        """Add endpoint"""
        name, instance = self._to_name_and_instance(endpoint)

        if name in self._endpoints:
            raise EndpointError(f"Endpoint with name '{name}' already exists")

        self._endpoints[name] = instance

    @final
    def delete(self, endpoint: str | type[WeatherEndpoint]):
        """Remove endpoint"""
        name = self._to_name(endpoint)

        if name not in self._endpoints:
            raise EndpointError(f"Endpoint with name '{name}' does not exist")

        del self._endpoints[name]

    @final
    def get(self, endpoint: str | type[WeatherEndpoint]) -> WeatherEndpoint:
        """Get endpoint by name"""
        name = self._to_name(endpoint)

        if result := self._endpoints.get(name):
            return result
        raise EndpointError(f"Endpoint with name '{name}' does not exist")

    @final
    def refresh(self, endpoint: str | type[WeatherEndpoint]):
        """Refresh data endpoint by name"""
        name = self._to_name(endpoint)

        if result := self._endpoints.get(name):
            result.refresh()
        raise EndpointError(f"Endpoint with name '{endpoint}' does not exist")

    def all(self) -> list[WeatherEndpoint]:
        """Get all endpoints"""
        return list(self._endpoints.values())
