from src.open_meteo.schemas import CurrentWeather, GeoList, Geo
from src.schemas import BasicWeather, ClarificationResponse, LocationOption, Coordinates


def toBasicWeather(current: CurrentWeather) -> BasicWeather:
    return BasicWeather(
        temperature=current.temperature,
        humidity=current.relative_humidity,
        wind_speed=current.wind_speed,
    )


def toLocationOption(geo: Geo) -> LocationOption:
    return LocationOption(
        id=geo.id,
        city=geo.name,
        country=geo.country,
        coordinates=Coordinates(latitude=geo.latitude, longitude=geo.longitude),
    )


def toDataGeoEndpointList(data: GeoList) -> ClarificationResponse:
    return ClarificationResponse(
        options=[toLocationOption(item) for item in data.results]
    )
