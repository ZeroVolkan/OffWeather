from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import final, Any
from loguru import logger

import itertools as it

from src.errors import EndpointError, CommandError
from src.static import apis
from src.utils import classproperty


@dataclass
class ConfigAPI(ABC):
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


class CommandAPI(ABC):
    @classproperty
    def name(cls) -> str:
        return cls.__name__

    @abstractmethod
    def __init__(self, api) -> None:
        self.api = api

    @abstractmethod
    def execute(self) -> Any:
        pass


class WeatherAPI(ABC):
    @classproperty
    def name(cls) -> str:
        return cls.__name__

    @abstractmethod
    def __init__(self, config: ConfigAPI):
        self.config = config

        self._endpoints: dict[str, WeatherEndpoint] = {}
        self._commands: dict[str, CommandAPI] = {}

        self.apis = apis()

        self._all_commands: dict[str, CommandAPI] = {
            command.name: command
            for command in it.chain(
                self.apis["WeatherAPI"]["commands"],
                self.apis[self.name]["commands"],
            )
        }

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
    def admin(self):
        """Not-save command for gets all commands"""
        self._commands.update({key: value(self) for key, value in self._all_commands.items()}) # type: ignore

    @final
    def execute(self, command: CommandAPI | str, *args, **kwargs):
        """Execute Command"""

        name = command.name if isinstance(command, CommandAPI) else command

        if result := self.commands.get(name):
            result.execute(*args, **kwargs)
        else:
            raise CommandError(f"Avalible command with name '{name}' does not exist")

    @property
    def commands(self):
        return self._commands

    @commands.setter
    def commands(self, value: str):
        if item := self._all_commands.get(value):
            self.commands[value] = item
        raise CommandError("This command don't exist in class")

    @commands.deleter
    def commands(self):
        del self._commands
        self._commands = dict()

    @property
    def endpoints(self):
        return self._endpoints

    @endpoints.setter
    def endpoints(self, value: str | WeatherEndpoint):
        self.add(value)

    @endpoints.deleter
    def endpoints(self):
        self._endpoints.clear()
