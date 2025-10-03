from __future__ import annotations
from abc import ABC, abstractmethod
from typing import final
from dataclasses import dataclass

from .api import WeatherAPI
from src.errors import ProcessorError, CommandError
from src.static import services
from src.utils import classproperty


@dataclass
class ServiceConfig(ABC):
    pass


class WeatherService(ABC):
    @classproperty
    def name(cls) -> str:
        return cls.__name__

    @abstractmethod
    def __init__(self, config: ServiceConfig):
        self.config: ServiceConfig = config

        self.available_commands: dict[str, CommandService] = {}
        self.processors: dict[str, WeatherProcessor] = {}

        self.services = services()

    @final
    def add(self, processor: str | WeatherProcessor):
        """Add processor to service"""
        name = processor.name if isinstance(processor, WeatherProcessor) else processor

        if name in self.processors:
            raise ProcessorError(f"Processor with name '{name}' already exists")

        if isinstance(processor, WeatherProcessor):
            self.processors[name] = processor
        else:
            self.processors[name] = self.services[self.name]["processors"][name](self)

    @final
    def delete(self, processor: str | WeatherProcessor):
        """Remove processor from service"""
        name = processor.name if isinstance(processor, WeatherProcessor) else processor

        if name not in self.processors:
            raise ProcessorError(f"Processor with name '{name}' does not exist")
        del self.processors[name]

    @final
    def get(self, name: str) -> WeatherProcessor:
        """Get processor by name"""
        if name not in self.processors:
            raise ProcessorError(f"Processor with name '{name}' does not exist")
        return self.processors[name]

    @final
    def execute(self, command: CommandService | str):
        """Execute API"""

        name = command.name if isinstance(command, CommandService) else command

        if result := self.available_commands.get(name):
            result.execute()
        else:
            raise CommandError(f"Avalible command with name '{name}' does not exist")


class WeatherProcessor[T: WeatherAPI](ABC):
    def __init__(self, **kwargs):
        self.name: str = self.__class__.__name__
        self._associations: dict[str, WeatherProcessor] = {}
        self.data = []

    @abstractmethod
    def run(self):
        """Process data from endpoints and pass to buffer for further processing"""
        pass

    @abstractmethod
    def save(self):
        """Save data to database"""
        pass

    @property
    def associations(self):
        return self._associations

    @associations.setter
    def associations(self, processor: WeatherProcessor):
        self._associations[processor.name] = processor



class CommandService:
    @abstractmethod
    def __init__(self, api) -> None:
        self.name: str = self.__class__.__name__
        self.api = api

    @abstractmethod
    def execute(self):
        pass
