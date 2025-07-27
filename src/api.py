from abc import ABC, abstractmethod


class WeatherAPI(ABC):
    def __init__(self, api, **kwargs):
        self.endpoints: dict[str, WeatherEndpoint] = {}
        self._init(api, **kwargs)

    @abstractmethod
    def _init(self, api, **kwargs):
        pass

    def add_strategy(self, strategy):
        self.endpoints[strategy.name] = strategy

    def delete_strategy(self, strategy):
        self.endpoints.pop(strategy.name)

    def refresh(self):
        "Обновляет данные у всех endpoints"
        for endpoint in self.endpoints.values():
            endpoint.refresh()

class WeatherEndpoint(ABC):
    def __init__(self):
        self.name: str = self.__class__.__name__
        self.data = []

    @abstractmethod
    def refresh(self):
        """Обновляет данные у переменных данных, которые хранят данные погоды"""
        pass
