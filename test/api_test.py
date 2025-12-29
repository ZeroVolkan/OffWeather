from __future__ import annotations
from src.core.api import StateAPI, BaseAPI, WeatherEndpoint, ConfigAPI
from src.errors import APIError

from dataclasses import dataclass


import pytest


@dataclass
class TestConfigAPI(ConfigAPI):
    secret: bool


class UnknownStateAPI(StateAPI):
    def __init__(self, api: TestWeatherAPI):
        super().__init__(api)
        self.api = api

    def check(self):
        """Check safe of transaction"""
        pass


class UpStateAPI(StateAPI):
    def __init__(self, api: TestWeatherAPI):
        super().__init__(api)
        self.api = api

    def check(self):
        """Check safe of transaction"""
        self.api.bar = True
        raise APIError("Test error")


class DownStateAPI(StateAPI):
    capable: list[type[StateAPI]] = [UpStateAPI]

    def __init__(self, api: TestWeatherAPI):
        super().__init__(api)

    def check(self):
        """Check safe of transaction"""
        pass


class TestWeatherAPI(BaseAPI):
    def __init__(self, config: TestConfigAPI, init_state=DownStateAPI):
        super().__init__(config, init_state=init_state)
        self.secret = config.secret
        self.foo = False
        self.bar = False

    def to(self, state: type[StateAPI]):
        self._state.to(state(self))

    def check(self):
        """Check safe of transaction"""
        self.foo = True


class GiveMeHelloEndpoint(WeatherEndpoint):
    def __init__(self, api: BaseAPI):
        super().__init__(api)
        self.data = {}
        self._secret = True

    def refresh(self):
        """Refresh endpoint"""
        self.data = {"message": "Hello"}

    def check(self):
        """Check safe of transaction"""
        if self._secret:
            raise APIError("This endpoint is secret")



class TestCoreAPI:
    def test_init(self):
        api = TestWeatherAPI(TestConfigAPI(True))
        api.check()
        assert api.foo == True
        assert api.secret == True


    def test_change_state(self):
        api = TestWeatherAPI(TestConfigAPI(True))
        api.check()
        assert api.foo == True
        assert api.secret == True

        with pytest.raises(APIError, match=f"Can't change state from DownStateAPI to UnknownStateAPI"):
            api.to(UnknownStateAPI)

        with pytest.raises(APIError, match="Test error"):
            api.to(UpStateAPI)


    def test_endpoint(self):
        api = TestWeatherAPI(TestConfigAPI(True))

        api.add(GiveMeHelloEndpoint)
        end = api.get(GiveMeHelloEndpoint)
        assert end.data == {}
        end.refresh()
        assert end.data == {"message": "Hello"}
