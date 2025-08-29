from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import final, Any
from loguru import logger

from .errors import EndpointError, CommandError
from .command import Command


@dataclass
class ConfigAPI(ABC):
    pass


class CommandAPI(Command):
    def __init__(self, api: WeatherAPI) -> None:
        super().__init__()
        self.api = api

    @abstractmethod
    def execute(self):
        pass


class WeatherAPI(ABC):
    @abstractmethod
    def __init__(self, config: ConfigAPI):
        self.name: str = self.__class__.__name__
        self.config = config

        self.endpoints: dict[str, WeatherEndpoint] = {}
        self.available_commands: dict[str, Command] = {}

    @final
    def add_endpoint(self, endpoint: WeatherEndpoint):
        """Add endpoint"""
        if endpoint.name in self.endpoints:
            raise EndpointError(f"Endpoint with name '{endpoint.name}' already exists")
        self.endpoints[endpoint.name] = endpoint

    @final
    def delete_endpoint(self, endpoint: WeatherEndpoint):
        """Remove endpoint"""
        if endpoint.name not in self.endpoints:
            raise EndpointError(f"Endpoint with name '{endpoint.name}' does not exist")
        del self.endpoints[endpoint.name]

    @final
    def get_endpoint(self, name: str) -> WeatherEndpoint:
        """Get endpoint by name"""
        if result := self.endpoints.get(name):
            return result
        raise EndpointError(f"Endpoint with name '{name}' does not exist")

    @final
    def refresh(self):
        """Refresh data for all endpoints"""
        logger.info(f"Refreshing endpoints {self.__class__.__name__}")
        for endpoint in self.endpoints.values():
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
    def execute(self, command: Command | str):
        """Execute Command"""

        name = command.name if isinstance(command, Command) else command

        if result := self.available_commands.get(name):
            result.execute()
        else:
            raise CommandError(f"Avalible command with name '{name}' does not exist")


class WeatherEndpoint[T: WeatherAPI](ABC):
    @abstractmethod
    def __init__(self, api: T):
        self.name: str = self.__class__.__name__
        self.api: T = api
        self.data: dict[str, Any] = {}
        logger.info(f"Initialized endpoint {self.name} with attributes {self.__dict__}")
        self.check()

    @abstractmethod
    def refresh(self):
        """Update data for variables that store weather data"""
        pass

    @abstractmethod
    def check(self):
        """Check Endpoint"""
        pass
