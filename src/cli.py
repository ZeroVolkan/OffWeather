import cmd
from loguru import logger
from typing import cast
from types import UnionType

from .api import WeatherAPI, ConfigAPI
from .setting import Setting
from .errors import ApiError, EndpointError, ConfigError
from .utils import unwrap_and_cast, unwrap_union_type
from .static import apis


class DebugShell(cmd.Cmd):
    prompt = "(debug) "
    intro = "Debug Shell for managing weather APIs"

    def __init__(self):
        super().__init__()
        self.api: WeatherAPI | None = None
        self.config: ConfigAPI | None = None
        self.selected: str | None = None
        self.setting: Setting = Setting("setting.toml")
        logger.add(".log/debug.log")
        logger.info("Debug shell started")

        self.apis = apis()

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
                if api_name not in self.apis.keys():
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
                    self.api = self.apis[self.selected]["class"](self.config)
                    logger.info(f"Created instance for API: {self.selected}")
                except ApiError as e:
                    print(f"Failed to create instance for API '{self.selected}': {e}")
                except AttributeError as e:
                    print(f"Failed to find API'{self.selected}': {e}")
            case "down":
                if self.selected is None:
                    print("No API selected.")
                    return
                if self.api:
                    del self.api
                    self.api = None
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

        api = self.apis.get(self.selected)

        if not api:
            print(f"❌ API '{self.selected}' not found")
            return

        SelectedConfig = api["config"]

        if not SelectedConfig:
            print(f"❌ Configuration not found for API '{self.selected}'")
            return

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
                    logger.info(
                        f"Configuration {SelectedConfig.__name__} saved to {path}"
                    )
                except ConfigError as e:
                    print(f"❌ {e}")
            case "fetch":
                if not path:
                    print("❌ Please provide a path to fetch the configuration")
                    return
                try:
                    self.config = self.setting.fetch(SelectedConfig, path)
                    logger.info(
                        f"Configuration {SelectedConfig.__name__} fetched from {path}"
                    )
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
                    setattr(
                        self.config,
                        param,
                        unwrap_and_cast(unwrap_union_type(annotation), value),
                    )
                except (ValueError, TypeError) as e:
                    print(f"❌ {e}")

                if not value:
                    logger.info(
                        f"Configuration {SelectedConfig.__name__} clear {param}"
                    )
                else:
                    logger.info(
                        f"Configuration {SelectedConfig.__name__} set {param} to {value}"
                    )
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
            data = self.api.get(endpoint or "GeoEndpoint").data
            logger.info(f"Data retrieved from {endpoint}")
            print(f"Data {endpoint}: {data}")
        except EndpointError as e:
            logger.error(f"Error getting data from {endpoint}: {e}")
            print(f"❌ Error getting data from {endpoint}: {e}")

    def do_status(self, args):
        """Show status cli"""
        pass

    def do_exit(self, args):
        """Exit the debug shell."""
        logger.info("Debug shell stopped")
        return 1


if __name__ == "__main__":
    DebugShell().cmdloop()
