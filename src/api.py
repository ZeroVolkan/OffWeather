from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import final, Any
from loguru import logger

from .errors import EndpointError, CommandError
from .static import apis


@dataclass
class ConfigAPI(ABC):
    pass


class WeatherAPI(ABC):
    @abstractmethod
    def __init__(self, config: ConfigAPI):
        self.name: str = self.__class__.__name__
        self.config = config

        self._endpoints: dict[str, WeatherEndpoint] = {}
        self._commands: dict[str, CommandAPI] = {}

        self.apis = apis()

    @final
    def add(self, endpoint: str | WeatherEndpoint):
        """Add endpoint"""
        name = endpoint.name if isinstance(endpoint, WeatherEndpoint) else endpoint

        if name in self._endpoints:
            raise EndpointError(f"Endpoint with name '{name}' already exists")

        if isinstance(endpoint, WeatherEndpoint):
            self._endpoints[name] = endpoint
        else:
            self._endpoints[name] = self.apis[self.name]["endpoints"][name](self)

    @final
    def delete(self, endpoint: str | WeatherEndpoint):
        """Remove endpoint"""
        name = endpoint.name if isinstance(endpoint, WeatherEndpoint) else endpoint

        if name not in self._endpoints:
            raise EndpointError(f"Endpoint with name '{name}' does not exist")
        del self._endpoints[name]

    @final
    def get(self, endpoint: str | WeatherEndpoint) -> WeatherEndpoint:
        """Get endpoint by name"""
        name = endpoint.name if isinstance(endpoint, WeatherEndpoint) else endpoint

        if result := self._endpoints.get(name):
            return result
        raise EndpointError(f"Endpoint with name '{name}' does not exist")

    @final
    def refresh(self):
        """Refresh data for all endpoints"""
        logger.info(f"Refreshing endpoints {self.__class__.__name__}")
        for endpoint in self._endpoints.values():
            endpoint.refresh()

    @abstractmethod
    def check(self):
        """Check API settings"""
        pass

    @abstractmethod
    def up(self):
        """Start API"""
        pass

    @final
    def execute(self, command: CommandAPI | str):
        """Execute Command"""

        name = command.name if isinstance(command, CommandAPI) else command

        if result := self._commands.get(name):
            result.execute()
        else:
            raise CommandError(f"Avalible command with name '{name}' does not exist")

    @property
    def commands(self):
        return self._commands

    @property
    def endpoints(self):
        return self._endpoints


class WeatherEndpoint(ABC):
    @abstractmethod
    def __init__(self, api):
        self.name: str = self.__class__.__name__
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


class CommandAPI:
    @abstractmethod
    def __init__(self, api) -> None:
        self.name: str = self.__class__.__name__
        self.api = api

    @abstractmethod
    def execute(self) -> Any:
        pass
