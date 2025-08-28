def apis():
    from src.open_meteo.api import OpenMeteoAPI, OpenMeteoConfig
    return {
        "open_meteo": {
            "class": OpenMeteoAPI,
            "config": OpenMeteoConfig,
        },
        # Add new APIs here
    }
