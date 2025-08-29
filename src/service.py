from __future__ import annotations
from abc import ABC, abstractmethod
from typing import final
from dataclasses import dataclass

from .api import WeatherAPI
from .errors import ProcessorError, CommandError
from .command import Command


@dataclass
class ConfigService(ABC):
    pass


class WeatherService(ABC):
    @abstractmethod
    def __init__(self, config: ConfigService):
        self.name: str = self.__class__.__name__
        self.config: ConfigService = config

        self.available_commands: dict[str, Command] = {}
        self.processors: dict[str, WeatherProcessor] = {}

    @final
    def add_processor(self, processor: WeatherProcessor):
        """Add processor"""
        if processor.name in self.processors:
            raise ProcessorError(
                f"Processor with name '{processor.name}' already exists"
            )
        self.processors[processor.name] = processor

    @final
    def delete_processor(self, processor: WeatherProcessor):
        """Remove processor"""
        if processor.name not in self.processors:
            raise ProcessorError(
                f"Processor with name '{processor.name}' does not exist"
            )
        del self.processors[processor.name]

    @final
    def get_processor(self, name: str) -> WeatherProcessor:
        """Get processor by name"""
        if result := self.processors.get(name):
            return result
        raise ProcessorError(f"Processor with name '{name}' does not exist")

    @final
    def execute(self, command: Command | str):
        """Execute API"""

        name = command.name if isinstance(command, Command) else command

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

    @associations.deleter
    def associations(self, processor: WeatherProcessor):
        del self._associations[processor.name]
