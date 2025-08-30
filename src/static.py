def apis():
    from src.open_meteo.api import OpenMeteoAPI, OpenMeteoConfig
    from src.open_meteo.forecast import ForecastEndpoint
    from src.open_meteo.geo import GeoEndpoint

    return {
        "OpenMeteoAPI": {
            "class": OpenMeteoAPI,
            "config": OpenMeteoConfig,
            "endpoints": [ForecastEndpoint, GeoEndpoint],
        },
        # Add new APIs here
    }


def services():
    from src.service import WeatherService, WeatherProcessor, ServiceConfig

    return {
        "WeatherService": {
            "class": WeatherService,
            "config": ServiceConfig,
            "processors": [
                WeatherProcessor,
            ],
        }
    }
