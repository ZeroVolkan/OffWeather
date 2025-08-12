from pydantic import BaseModel


# TEMP:
class Weather(BaseModel):
    pass


class CurrentWeather(BaseModel):
    temperature: float
    humidity: float
    wind_speed: float
    pressure: int
    weather: str
