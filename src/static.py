def apis():
    from src.core.api import WeatherAPI, ConfigAPI

    from src.open_meteo.api import OpenMeteoAPI, OpenMeteoConfig
    from src.open_meteo.forecast import ForecastEndpoint
    from src.open_meteo.geo import GeoEndpoint

    return {
        "WeatherAPI": {
            "class": WeatherAPI,
            "config": ConfigAPI,
            "endpoints": [],
        },
        "OpenMeteoAPI": {
            "class": OpenMeteoAPI,
            "config": OpenMeteoConfig,
            "endpoints": {
                "forecast": ForecastEndpoint,
                "geo": GeoEndpoint,
            },
        },
        # Add new APIs here
    }


def workflows():
    from src.workflow import basis

    return {
        "basis": {"description": "Base workflow for weather data", "executable": basis}
    }
