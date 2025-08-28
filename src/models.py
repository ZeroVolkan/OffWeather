from pydantic import BaseModel
from typing import List, Union
from abc import ABC


class Coordinates(BaseModel):
    latitude: float
    longitude: float


class BasicWeather(BaseModel):
    temperature: float
    humidity: float
    wind_speed: float


class ExtendedWeather(BaseModel, ABC):
    pass


# ----- Various responses -----
class LocationOption(BaseModel):
    id: int
    city: str
    country: str
    coordinates: Coordinates


class ClarificationResponse(BaseModel):
    options: List[LocationOption]


class FullDataResponse(BaseModel):
    location: LocationOption
    basic_weather: BasicWeather
    extended_weather: ExtendedWeather


# ----- Universal response -----
OpenMeteoResponse = Union[ClarificationResponse, FullDataResponse]
