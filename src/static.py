def apis():
    from src.core.api import WeatherAPI, ConfigAPI
    from src.core.commands import Add, Refresh, Delete, Data

    from src.open_meteo.api import OpenMeteoAPI, OpenMeteoConfig
    from src.open_meteo.forecast import ForecastEndpoint
    from src.open_meteo.geo import GeoEndpoint
    from src.open_meteo.commands import SelectGeo

    return {
        "WeatherAPI": {
            "class": WeatherAPI,
            "config": ConfigAPI,
            "endpoints": [],
            "commands": [Add, Refresh, Delete, Data],
        },
        "OpenMeteoAPI": {
            "class": OpenMeteoAPI,
            "config": OpenMeteoConfig,
            "endpoints": [ForecastEndpoint, GeoEndpoint],
            "commands": [SelectGeo],
        },
        # Add new APIs here
    }


def services():
    from src.core.service import WeatherService, WeatherProcessor, ServiceConfig

    return {
        "WeatherService": {
            "class": WeatherService,
            "config": ServiceConfig,
            "processors": [
                WeatherProcessor,
            ],
        }
    }


def workflows():
    from src.workflow import basis

    return {
        "basis": {
            "description": "Base workflow for weather data",
            "executable": basis
        }
    }
