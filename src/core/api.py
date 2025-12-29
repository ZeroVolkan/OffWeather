from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from src.errors import EndpointError
from src.static import apis
from abc import ABC, abstractmethod


@dataclass
class ConfigAPI(ABC):
    pass



class BaseState(ABC):
    @classmethod
    def name(cls) -> str:
        return cls.__name__

    @abstractmethod
    def __init__(self, api: "BaseAPI") -> None:
        self.api = api

    def to(self, state: BaseState) -> None:
        self.api._state = state

    @abstractmethod
    def run(self) -> Any: ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.api})"


class BaseEndpoint(ABC):
    @abstractmethod
    def __init__(self, api: "BaseAPI") -> None:
        self.api = api
        self.data = {}

    @classmethod
    def name(cls) -> str:
        return cls.__name__

    @abstractmethod
    def refresh(self) -> None: ...
    @abstractmethod
    def check(self) -> None: ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.api})"


@dataclass
class BaseAPI:
    config: ConfigAPI
    init_state: type[BaseState]
    data: dict

    def __post_init__(self) -> None:
        self.apis = apis()
        self._endpoints: dict[str, BaseEndpoint] = dict()
        self._state: BaseState = self.init_state(self)

    @classmethod
    def name(cls) -> str:
        return cls.__name__

    @property
    def state(self) -> BaseState:
        return self._state

    def to(self, state: type[BaseState]) -> None:
        new = state(self)
        self._state.to(new)

    def run(self, **kwargs) -> Any:
        return self._state.run(**kwargs)

    def _to_name_and_instance(
        self, endpoint: str | type[BaseEndpoint]
    ) -> tuple[str, BaseEndpoint]:
        if isinstance(endpoint, type) and issubclass(endpoint, BaseEndpoint):
            return endpoint.name(), endpoint(self)
        if isinstance(endpoint, str):
            return endpoint, self.apis[self.name()]["endpoints"][endpoint](self)
        raise TypeError(f"Invalid endpoint type: {type(endpoint)}")

    def _to_name(self, endpoint: str | type[BaseEndpoint]) -> str:
        if isinstance(endpoint, type) and issubclass(endpoint, BaseEndpoint):
            return endpoint.name()
        if isinstance(endpoint, str):
            return endpoint
        raise TypeError(f"Invalid endpoint type: {type(endpoint)}")

    def add(self, endpoint: str | type[BaseEndpoint]) -> None:
        name, instance = self._to_name_and_instance(endpoint)
        if name in self._endpoints:
            raise EndpointError(f"Endpoint with name '{name}' already exists")
        self._endpoints[name] = instance

    def delete(self, endpoint: str | type[BaseEndpoint]) -> None:
        name = self._to_name(endpoint)
        if name not in self._endpoints:
            raise EndpointError(f"Endpoint with name '{name}' does not exist")
        del self._endpoints[name]

    def get(self, endpoint: str | type[BaseEndpoint]) -> BaseEndpoint:
        name = self._to_name(endpoint)
        if result := self._endpoints.get(name):
            return result
        raise EndpointError(f"Endpoint with name '{name}' does not exist")

    def refresh(self, endpoint: str | type[BaseEndpoint]) -> None:
        name = self._to_name(endpoint)
        if result := self._endpoints.get(name):
            result.refresh()
        else:
            raise EndpointError(f"Endpoint with name '{endpoint}' does not exist")

    def all(self) -> list[BaseEndpoint]:
        return list(self._endpoints.values())
