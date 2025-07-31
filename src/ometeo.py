import requests
from requests_cache import CachedSession
from retry_requests import retry

from api import WeatherAPI, WeatherEndpoint


class OpenMeteoAPI(WeatherAPI):
    def setup(self, config, **kwargs):
        self.config = config
        self.session: requests.Session = retry(
            CachedSession(".cache", expire_after = 3600),
            retries = 5, backoff_factor = 0.2
        )
        self.add_endpoint(GetCurrentWeather(self))

    def setting(self, **kwargs):
        """Меняет настройки API"""
        pass

class GetCurrentWeather[OpenMeteoAPI](WeatherEndpoint):
    def setup(self, **kwargs):
        self.url = "https://api.open-meteo.com/v1/forecast"

        self.latitude = kwargs.get("latitude", 52.52)
        self.longitude = kwargs.get("longitude", 13.41)

    def refresh(self):
        session: requests.Session = self.api.session

        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
           	"timeformat": "unixtime",
            "current": "temperature_2m",
        }

        response = session.get(self.url, params=params)

        if response.status_code == 200:
            json_data = response.json()
            current = json_data.get("current", {})
            temperature = current.get("temperature_2m")
            timestamp = current.get("time")

            if temperature is not None:
                self.data.append({
                    "temperature_2m": temperature,
                    "time": timestamp
                })
        else:
            print(f"Ошибка API: {response.status_code}") # TEMP


# TEMPORALY TESTING
if __name__ == "__main__":
    api = OpenMeteoAPI("None")
    api.refresh()
    print(api.endpoints["GetCurrentWeather"].data[0])
