from loguru import logger

from .api import OpenMeteoAPI
from .geo import DataGeoEndpointList

from src.core.api import CommandAPI
from src.errors import SettingError, CommandError
from src.models import Coordinates


class SelectGeo(CommandAPI):
    def __init__(self, api: OpenMeteoAPI) -> None:
        self.api: OpenMeteoAPI = api

    def execute(self, id: int | None = None):
        geo = self.api.get("GeoEndpoint")

        try:
            data: DataGeoEndpointList = geo.data["DataGeoEndpointList"]
        except KeyError:
            logger.error(f"{geo.name} data not found")
            raise CommandError(f"{geo.name} data not found")

        if self.api.id is None or id is None:
            logger.error("Please set id")
            raise SettingError("Please set id")

        id = id if id else self.api.id

        for result in data.results:
            if result.id == id:
                self.api.id = result.id
                self.api.city = result.name
                self.api.country = result.country
                self.api.coordinates = Coordinates(
                    latitude=result.latitude, longitude=result.longitude
                )
                self.api.delete("GeoEndpoint")
                logger.info(
                    f"Deleted {geo.name}, changes attribute city={result.name}, country={result.country}, coordinates={self.api.coordinates}"
                )
                return result
        else:
            logger.error(f"No matching id found, id={id}")
            raise CommandError(f"No matching id found, id={id}")
