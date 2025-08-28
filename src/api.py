from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import final, Any
from loguru import logger

from .errors import EndpointError, ProcessorError


class WeatherAPI(ABC):
    @abstractmethod
    def __init__(self, **kwargs):
        self.endpoints: dict[str, WeatherEndpoint] = {}
        self.processors: dict[str, WeatherProcessor] = {}

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
    def refresh(self):
        """Refresh data for all endpoints"""
        logger.info(f"Refreshing endpoints {self.__class__.__name__}")
        for endpoint in self.endpoints.values():
            endpoint.refresh()

    @final
    def process(self):
        """Process data from endpoints and pass to unified data model"""
        logger.info(f"Processing data from endpoints {self.__class__.__name__}")
        for processor in self.processors.values():
            processor.run()

    @final
    def save(self):
        """Save data to database"""
        logger.info(f"Saving data from processors {self.__class__.__name__}")
        for processor in self.processors.values():
            processor.save()

    @abstractmethod
    def setting(self, resetup: bool = False, **kwargs):
        """Change API settings"""
        pass

    @abstractmethod
    def check(self):
        """Check API settings"""
        pass

    @abstractmethod
    def up(self):
        pass


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


@dataclass
class Config(ABC):
    pass
