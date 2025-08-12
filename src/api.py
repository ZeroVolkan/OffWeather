from __future__ import annotations
from abc import ABC, abstractmethod
from typing import final, Any

from loguru import logger


class WeatherAPI(ABC):
    @abstractmethod
    def __init__(self, **kwargs):
        self.endpoints: dict[str, WeatherEndpoint] = {}
        self.processors: dict[str, WeatherProcessor] = {}

    @final
    def add_endpoint(self, endpoint: WeatherEndpoint):
        """Добавляет endpoint"""
        if endpoint.name in self.endpoints:
            raise ValueError(f"Endpoint with name '{endpoint.name}' already exists")
        self.endpoints[endpoint.name] = endpoint

    @final
    def delete_endpoint(self, endpoint: WeatherEndpoint):
        """Удаляет endpoint"""
        if endpoint.name not in self.endpoints:
            raise ValueError(f"Endpoint with name '{endpoint.name}' does not exist")
        del self.endpoints[endpoint.name]

    @final
    def get_endpoint(self, name: str) -> WeatherEndpoint:
        """Получает endpoint по имени"""
        if result := self.endpoints.get(name):
            return result
        raise ValueError(f"Endpoint with name '{name}' does not exist")

    @final
    def add_processor(self, processor: WeatherProcessor):
        """Добавляет процессор"""
        if processor.name in self.processors:
            raise ValueError(f"Processor with name '{processor.name}' already exists")
        self.processors[processor.name] = processor

    @final
    def delete_processor(self, processor: WeatherProcessor):
        """Удаляет процессор"""
        if processor.name not in self.processors:
            raise ValueError(f"Processor with name '{processor.name}' does not exist")
        del self.processors[processor.name]

    @final
    def get_processor(self, name: str) -> WeatherProcessor:
        """Получает процессор по имени"""
        if result := self.processors.get(name):
            return result
        raise ValueError(f"Processor with name '{name}' does not exist")

    @final
    def refresh(self):
        """Обновляет данные у всех endpoints"""
        logger.info(f"Refreshing endpoints {self.__class__.__name__}")
        for endpoint in self.endpoints.values():
            endpoint.refresh()

    @final
    def process(self):
        """Обрабатывают данныe из endpoints и передают в единую модель данных"""
        logger.info(f"Processing data from endpoints {self.__class__.__name__}")
        for processor in self.processors.values():
            processor.run(self.endpoints)

    @abstractmethod
    def setting(self, **kwargs):
        """Меняет настройки API"""
        pass

    @abstractmethod
    def check(self):
        """Проверяет настройки API"""
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
        """Обновляет данные у переменных данных, которые хранят данные погоды"""
        pass

    @abstractmethod
    def check(self):
        """Проверяет настройки Endpoint"""
        pass


class WeatherProcessor[T: WeatherAPI](ABC):
    def __init__(self, **kwargs):
        self.name: str = self.__class__.__name__
        self.data = []

    @abstractmethod
    def run(self, endpoints: dict[str, T]):
        """Обрабатывает данные из endpoints и передает в единую модель данных"""
        pass
