def apis():
    from src.core.api import BaseAPI, ConfigAPI

    from src.open_meteo.api import OpenMeteoAPI, OpenMeteoConfig
    from src.open_meteo.forecast import ForecastEndpoint
    from src.open_meteo.geo import GeoEndpoint

    return {
        "BaseAPI": {
            "class": BaseAPI,
            "config": ConfigAPI,
            "endpoints": {},
            "paths": {},
        },
        "OpenMeteoAPI": {
            "class": OpenMeteoAPI,
            "config": OpenMeteoConfig,
            "endpoints": {
                "ForecastEndpoint": ForecastEndpoint,
                "GeoEndpoint": GeoEndpoint,
            },
            "paths": {"InitMeteoState": set()},
        },
        # Add new APIs here
    }


def workflows():
    from src.workflow import basis

    return {
        "basis": {"description": "Base workflow for weather data", "executable": basis}
    }
