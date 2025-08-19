from pydantic import BaseModel
from enum import Enum
from typing import List, Union


# ----- Enum кодов погоды -----
class WeatherCode(Enum):
    CLEAR_SKY = 0
    MAINLY_CLEAR = 1
    PARTLY_CLOUDY = 2
    OVERCAST = 3
    FOG = 45
    DEPOSITING_RIME_FOG = 48
    DRIZZLE_LIGHT = 51
    DRIZZLE_MODERATE = 53
    DRIZZLE_DENSE = 55
    FREEZING_DRIZZLE_LIGHT = 56
    FREEZING_DRIZZLE_DENSE = 57
    RAIN_SLIGHT = 61
    RAIN_MODERATE = 63
    RAIN_HEAVY = 65
    FREEZING_RAIN_LIGHT = 66
    FREEZING_RAIN_HEAVY = 67
    SNOW_SLIGHT = 71
    SNOW_MODERATE = 73
    SNOW_HEAVY = 75
    SNOW_GRAINS = 77
    RAIN_SHOWERS_SLIGHT = 80
    RAIN_SHOWERS_MODERATE = 81
    RAIN_SHOWERS_VIOLENT = 82
    SNOW_SHOWERS_SLIGHT = 85
    SNOW_SHOWERS_HEAVY = 86
    THUNDERSTORM_SLIGHT_MODERATE = 95
    THUNDERSTORM_SLIGHT_HAIL = 96
    THUNDERSTORM_HEAVY_HAIL = 99

    def description(self) -> str:
        return {
            WeatherCode.CLEAR_SKY: "Clear sky",
            WeatherCode.MAINLY_CLEAR: "Mainly clear",
            WeatherCode.PARTLY_CLOUDY: "Partly cloudy",
            WeatherCode.OVERCAST: "Overcast",
            WeatherCode.FOG: "Fog",
            WeatherCode.DEPOSITING_RIME_FOG: "Depositing rime fog",
            WeatherCode.DRIZZLE_LIGHT: "Drizzle: Light",
            WeatherCode.DRIZZLE_MODERATE: "Drizzle: Moderate",
            WeatherCode.DRIZZLE_DENSE: "Drizzle: Dense",
            WeatherCode.FREEZING_DRIZZLE_LIGHT: "Freezing drizzle: Light",
            WeatherCode.FREEZING_DRIZZLE_DENSE: "Freezing drizzle: Dense",
            WeatherCode.RAIN_SLIGHT: "Rain: Slight",
            WeatherCode.RAIN_MODERATE: "Rain: Moderate",
            WeatherCode.RAIN_HEAVY: "Rain: Heavy",
            WeatherCode.FREEZING_RAIN_LIGHT: "Freezing rain: Light",
            WeatherCode.FREEZING_RAIN_HEAVY: "Freezing rain: Heavy",
            WeatherCode.SNOW_SLIGHT: "Snow fall: Slight",
            WeatherCode.SNOW_MODERATE: "Snow fall: Moderate",
            WeatherCode.SNOW_HEAVY: "Snow fall: Heavy",
            WeatherCode.SNOW_GRAINS: "Snow grains",
            WeatherCode.RAIN_SHOWERS_SLIGHT: "Rain showers: Slight",
            WeatherCode.RAIN_SHOWERS_MODERATE: "Rain showers: Moderate",
            WeatherCode.RAIN_SHOWERS_VIOLENT: "Rain showers: Violent",
            WeatherCode.SNOW_SHOWERS_SLIGHT: "Snow showers: Slight",
            WeatherCode.SNOW_SHOWERS_HEAVY: "Snow showers: Heavy",
            WeatherCode.THUNDERSTORM_SLIGHT_MODERATE: "Thunderstorm: Slight or moderate",
            WeatherCode.THUNDERSTORM_SLIGHT_HAIL: "Thunderstorm with slight hail",
            WeatherCode.THUNDERSTORM_HEAVY_HAIL: "Thunderstorm with heavy hail",
        }.get(self, "Unknown weather code")


# ----- Запрос -----
class Coordinates(BaseModel):
    latitude: float
    longitude: float


class GeoRequest(BaseModel):
    id: int | None = None
    city: str
    language: str
    country: str
    count: int = 1


class ForecastRequest(BaseModel):
    coordinates: Coordinates


# ----- Current -----
class CurrentWeather(BaseModel):
    weather_code: WeatherCode
    temperature: float
    apparent_temperature: float
    relative_humidity: float
    wind_speed: float
    wind_direction: float
    wind_gusts: float


# ----- Daily -----
class DailyWeather(BaseModel):
    date: int  # unixtime (timeformat=unixtime)
    weather_code: WeatherCode

    temperature_min: float
    temperature_max: float
    temperature_mean: float

    apparent_temperature_min: float
    apparent_temperature_max: float
    apparent_temperature_mean: float

    relative_humidity_min: float
    relative_humidity_max: float
    relative_humidity_mean: float

    wind_speed_min: float
    wind_speed_max: float
    wind_speed_mean: float

    wind_gusts_min: float
    wind_gusts_max: float
    wind_gusts_mean: float

    wind_direction_dominant: float


# ----- Основная модель -----
class Weather(BaseModel):
    current: CurrentWeather
    daily: List[DailyWeather]


# ----- Варианты ответов -----
class LocationOption(BaseModel):
    id: int
    city: str
    country: str
    coordinates: Coordinates


class ClarificationResponse(BaseModel):
    type: str = "clarification"
    options: List[LocationOption]


class FullDataResponse(BaseModel):
    type: str = "data"
    location: LocationOption
    weather: Weather


# ----- Универсальный ответ -----
OpenMeteoResponse = Union[ClarificationResponse, FullDataResponse]
