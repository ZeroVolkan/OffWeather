import cmd
from loguru import logger
from dataclasses import dataclass, asdict
from setting import Setting
from open_meteo.api import OpenMeteoAPI
from errors import ApiError, EndpointError, ConfigError


@dataclass
class OpenMeteoConfig:
    id: int | None = None
    api_key: str | None = None
    country: str | None = None
    city: str | None = None
    language: str | None = None
    count: int | None = None


class DebugShell(cmd.Cmd):
    prompt = "(debug) "
    intro = "Debug Shell"

    apis = {
        "open-meteo": {
            "class": OpenMeteoAPI,
            "config": OpenMeteoConfig,
        },
        # You can add other APIs here
        # "weather-api": {
        #     "class": "WeatherAPI",
        #     "config": "WeatherConfig",
        # },
    }

    def __init__(self):
        super().__init__()
        self.setting = Setting("setting.toml")
        self.config = None
        self.api = None  # instance of OpenMeteoConfig
        self.current_api = None
        self.current_config_class = None
        logger.add(".log/debug.log")
        logger.info("Debug shell started")

    def do_list(self, args=""):
        """Show avalible APIs"""
        print("Avalible apis:")
        for api_name, api_info in self.apis.items():
            status = "Active" if api_name == self.current_api else "Avalible"
            print(f"  {api_name} ({api_info['class']}) - {status}")

    def do_api(self, api_name):
        """Setting to API: api open-meteo"""
        if not api_name or api_name not in self.apis:
            self.do_list()
            return

        self.current_api = api_name
        logger.info(f"Setting to API: {api_name}")
        print(f"Setting to {api_name}")

    def do_config(self, *path):
        """Loading configuration: config open-meteo"""
        if self.api:
            print("API instance already exists, you need to delete it first")
            return
        if not self.current_api:
            print("❌ Choice API, use api")
            return

        config_class = self.apis[self.current_api]["config"]

        try:
            self.config = self.setting.fetch(config_class, [*path])
            self.current_config_class = config_class
            logger.info(f"Config loaded for {config_class.__name__}")
            print("Configuration loaded")
        except ConfigError as e:
            logger.error(f"Error loading config: {e}")
            print(f"❌ Error: {e}, create new config")
            self.config = config_class()
            self.current_config_class = config_class

    def do_up(self, args=""):
        """Create API instance"""
        if not self.config:
            print("❌ First load configuration")
            return

        if not self.current_api:
            print("❌ First switch to API")
            return

        try:
            self.apis[self.current_api]["class"](asdict(self.config))
            logger.info(f"API instance created for {self.current_api}")
            print("API created")
        except ApiError as e:
            logger.error(f"Error creating API: {e}")
            print(f"❌ Error creating API: {e}")

    def do_down(self, args=""):
        """Remove API instance"""
        self.api = None
        print("API instance removed")

    def do_refresh(self, args=""):
        """Refresh API"""
        if not self.api:
            print("❌ First create API")
            return

        try:
            self.api.refresh()
            logger.info("API data refreshed")
            print("Data refreshed")
        except ApiError as e:
            logger.error(f"Error refreshing API: {e}")
            print(f"❌ Error refreshing API: {e}")

    def do_show(self, endpoint):
        """Show data: show GeoEndpoint"""
        if not self.api:
            print("❌ First create API")
            return

        try:
            data = self.api.get_endpoint(endpoint or "GeoEndpoint").data
            logger.info(f"Data retrieved from {endpoint}")
            print(f"Data {endpoint}: {data}")
        except EndpointError as e:
            logger.error(f"Error getting data from {endpoint}: {e}")
            print(f"❌ Error getting data from {endpoint}: {e}")

    def do_set_config(self, args):
        """Change configuration parameter: set_config city Moscow"""
        if not self.config:
            print("❌ First load configuration")
            return

        parts = args.split(maxsplit=1)
        if len(parts) < 2:
            print("❌ Usage: set_config <parameter> <value>")
            return

        param, value = parts
        if value.lower() == "none":
            value = None
        elif param == "count" and value is not None:
            try:
                value = int(value)
            except ValueError:
                print(f"❌ Invalid value for count: {value}")
                return

        if hasattr(self.config, param):
            setattr(self.config, param, value)
            logger.info(f"Config parameter {param} set to {value}")
            print(f"{param} = {value}")
        else:
            print(f"❌ Unknown parameter: {param}")

    def do_save_config(self, args):
        """Save configuration"""
        if not self.config:
            print("❌ No configuration to save")
            return

        if not self.current_api:
            print("❌ No API selected")
            return

        try:
            self.setting.save(self.config, [self.current_api])
            logger.info(f"Config saved for {self.current_api}")
            print(f"Configuration saved for {self.current_api}")
        except ConfigError as e:
            logger.error(f"Error saving config: {e}")
            print(f"❌ Error saving: {e}")

    def do_status(self, args):
        """Show detailed status"""
        print("Status: ")
        print(f"  Current API: {self.current_api or 'not selected'}")
        if self.current_api and self.current_api in self.apis:
            api_info = self.apis[self.current_api]
            print(f"    API Class: {api_info['class']}")
            print(f"    Config: {api_info['config']}")

        print(f"  Configuration: {'loaded' if self.config else 'not loaded'}")
        if self.config:
            print(
                f"    Config Type: {self.current_config_class.__name__ if self.current_config_class else 'unknown'}"
            )
            for field_name in self.config.__annotations__.keys():
                field_value = getattr(self.config, field_name, "не найдено")
                if field_name == "api_key" and field_value:
                    field_value = "***скрыт***"
                print(f"    {field_name}: {field_value or 'не установлен'}")

        print(f"  API instance: {'создан' if self.api else 'не создан'}")
        if self.api:
            print(
                f"    Endpoints: {list(self.api.endpoints.keys()) if hasattr(self.api, 'endpoints') else 'н/д'}"
            )

        print(f"  Avaliable API: {len(self.apis)} ({', '.join(self.apis.keys())})")

    def do_quit(self, args):
        """Exit"""
        logger.info("Debug shell stopped")
        return True

    def do_processors(self, args):
        """List available processors"""
        logger.info("Listing available processors")
        if self.api:
            print(f"Available processors: {list(self.api.processors.keys())}")
        else:
            print("No API instance created")


if __name__ == "__main__":
    DebugShell().cmdloop()
