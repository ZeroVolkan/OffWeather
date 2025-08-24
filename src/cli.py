import cmd
from dataclasses import dataclass, asdict
from abc import ABC
from loguru import logger
from typing import cast
from types import UnionType

from .api import WeatherAPI
from .setting import Setting
from .open_meteo.api import OpenMeteoAPI
from .errors import ApiError, EndpointError, ConfigError
from .utils import unwrap_and_cast, unwrap_union_type


@dataclass
class Config(ABC):
    pass

@dataclass
class OpenMeteoConfig(Config):
    id: int | None = None
    api_key: str | None = None
    country: str | None = None
    city: str | None = None
    language: str | None = None
    count: int | None = None

class DebugShell(cmd.Cmd):
    prompt = "(debug) "
    intro = "Debug Shell for managing weather APIs"

    apis = {
        "open-meteo": {
            "class": OpenMeteoAPI,
            "config": OpenMeteoConfig,
        },
        # You can add other APIs here
    }

    def __init__(self):
        super().__init__()
        self.api: WeatherAPI | None = None
        self.config: Config | None = None
        self.selected: str | None = None
        self.setting: Setting = Setting("setting.toml")
        logger.add(".log/debug.log")
        logger.info("Debug shell started")

    def do_api(self, args):
        """Manage api

        Usage: api [select|list] <api_name>
        select <api_name> : Select an API
        list : List available APIs
        up: Instance Api create
        down: Instance Api delete
        """
        parts = args.split(maxsplit=2)

        command = parts[0] if parts else ""
        api_name = parts[1] if len(parts) > 1 else None

        match command:
            case "select":
                if api_name is None:
                    print("Please provide an API name.")
                    return
                if api_name not in self.apis:
                    print(f"API '{api_name}' not found.")
                    return
                self.selected = api_name
                logger.info(f"Selected API: {api_name}")
            case "list":
                print("Available APIs:")
                for api_name, api_info in self.apis.items():
                    print(f"  {api_name} ({api_info['class']})")
            case "up":
                if self.config is None:
                    print("No configuration loaded.")
                    return
                if self.selected is None:
                    print("No API selected.")
                    return
                try:
                    self.api = self.apis[self.selected]["class"](asdict(self.config))
                except ApiError as e:
                    print(f"Failed to create instance for API '{self.selected}': {e}")
                logger.info(f"Created instance for API: {self.selected}")
            case "down":
                if self.selected is None:
                    print("No API selected.")
                    return
                del self.api
                logger.info(f"Deleted instance for API: {self.selected}")
            case _:
                print("Invalid command.")
                print(self.do_api.__doc__)
                return


    def do_config(self, args):
        """Manage configuration settings.

        Usage: config [save|load|show|set|reset] [path|param value]
        - save [path] : Save configuration to TOML file
        - fetch [path] : Fetch configuration from TOML file
        - set [param] <value> : Set a configuration parameter
        - create : Create a new configuration file
        - show : Show current configuration
        - clear : Clear configuration
        """
        if not self.selected:
            print("❌ No API selected, please select an API first, use command api")
            return

        SelectedConfig = self.apis[self.selected]["config"]

        parts = args.split()
        command = parts[0] if parts else None

        path = parts[1:] if len(parts) > 1 else None

        param = parts[1] if len(parts) > 1 else None
        value = parts[2] if len(parts) > 2 else None

        if not command:
            print(self.do_config.__doc__)
            return

        match command:
            case "save":
                if not path:
                    print("❌ Please provide a path to save the configuration")
                    return
                try:
                    self.config = self.setting.save(SelectedConfig, path)
                    logger.info(f"Configuration {SelectedConfig.__name__} saved to {path}")
                except ConfigError as e:
                    print(f"❌ {e}")
            case "fetch":
                if not path:
                    print("❌ Please provide a path to fetch the configuration")
                    return
                try:
                    self.config = self.setting.fetch(SelectedConfig, path)
                    logger.info(f"Configuration {SelectedConfig.__name__} fetched from {path}")
                except ConfigError as e:
                    print(f"❌ {e}")
            case "set":
                if not param:
                    print("❌ Please provide a parameter")
                    return
                if not self.config:
                    print("X Please load or create a configuration")
                    return
                if not hasattr(self.config, param):
                    print(f"X Parameter {param} does not exist")
                    return

                annotation = cast(UnionType, self.config.__annotations__.get(param))

                try:
                    setattr(self.config, param, unwrap_and_cast(unwrap_union_type(annotation), value))
                except (ValueError, TypeError) as e:
                    print(f"❌ {e}")

                if not value:
                    logger.info(f"Configuration {SelectedConfig.__name__} clear {param}")
                else:
                    logger.info(f"Configuration {SelectedConfig.__name__} set {param} to {value}")
            case "create":
                if self.config:
                    print("❌ Configuration already exists")
                    return
                self.config = SelectedConfig()
                logger.info(f"Configuration {SelectedConfig.__name__} created")
            case "show":
                if not self.config:
                    print("❌ First load configuration")
                    return
                print(self.config)
            case "clear":
                if not self.config:
                    print("❌ Configuration isn't loaded")
                    return
                self.config = None
                logger.info(f"Configuration {SelectedConfig.__name__} cleared")
            case _:
                print("Invalid command.")
                print(self.do_api.__doc__)
                return


    def do_show(self, endpoint):
        """Show data from an endpoint: show GeoEndpoint"""
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

    def do_status(self, args):
        """Show detailed status of the shell."""
        print("Status: ")
        api_name = next((name for name, info in self.apis.items() if info["config"] == type(self.config)), None) if self.config else None
        print(f"  Current API: {api_name or 'not selected'}")
        if api_name and api_name in self.apis:
            api_info = self.apis[api_name]
            print(f"    API Class: {api_info['class']}")
            print(f"    Config: {api_info['config']}")
        print(f"  Configuration: {'loaded' if self.config else 'not loaded'}")
        if self.config:
            print(f"    Config Type: {type(self.config).__name__}")
            for field_name in self.config.__annotations__.keys():
                field_value = getattr(self.config, field_name, "not found")
                if field_name == "api_key" and field_value:
                    field_value = "***hidden***"
                print(f"    {field_name}: {field_value or 'not set'}")
        print(f"  API instance: {'created' if self.api else 'not created'}")
        if self.api:
            print(f"    API Type: {self.api.__class__.__name__}")
            print(f"    Endpoints: {list(self.api.endpoints.keys()) if hasattr(self.api, 'endpoints') else 'n/a'}")
        print(f"  Available APIs: {len(self.apis)} ({', '.join(self.apis.keys())})")

    def do_exit(self, args):
        """Exit the debug shell."""
        logger.info("Debug shell stopped")
        return True

    def do_processor(self, args):
        """List available processors."""
        logger.info("Listing available processors")
        if self.api:
            print(f"Available processors: {list(self.api.processors.keys())}")
        else:
            print("No API instance created")

    def do_endpoint(self, args):
        """List available endpoints."""
        logger.info("Listing available endpoints")
        if self.api:
            print(f"Available endpoints: {list(self.api.endpoints.keys())}")
        else:
            print("No API instance created")

if __name__ == "__main__":
    DebugShell().cmdloop()
