import cmd
from dataclasses import dataclass, asdict
from abc import ABC
from loguru import logger
from api import WeatherAPI
from setting import Setting
from open_meteo.api import OpenMeteoAPI
from errors import ApiError, EndpointError, ConfigError

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
        self.setting: Setting = Setting("setting.toml")
        self.config: Config | None = None
        self.api: WeatherAPI | None = None
        logger.add(".log/debug.log")
        logger.info("Debug shell started")

    def do_list(self, args=""):
        """List available APIs."""
        print("Available APIs:")
        for api_name, api_info in self.apis.items():
            print(f"  {api_name} ({api_info['class']})")

    def do_config(self, args):
        """Manage configuration settings.

        Usage: config [save|load|show|set|reset] [api_name] [path|param value]
        - save [api_name] [path] : Save configuration to TOML file
        - load [api_name] [path] : Load configuration from TOML file
        - show : Show current configuration
        - set [api_name] [param] <value> : Set a configuration parameter
        - reset : Clear configuration
        """
        parts = args.split(maxsplit=3)
        command = parts[0] if parts else ""
        api_name = parts[1] if len(parts) > 1 else None
        extra = parts[2:] if len(parts) > 2 else []
        params = parts[1:] if len(parts) > 1 else []

        if not command:
            print("❌ Usage: config [save|load|show|set|reset] [api_name] [path|param value]")
            print("  save [api_name] <path> - Save configuration")
            print("  load [api_name] <path> - Load configuration")
            print("  show - Display current configuration")
            print("  set [api_name] [param] <value> - Set configuration parameter")
            print("  reset - Clear configuration")
            return

        if command not in ["load", "reset", "show"] and not self.config:
            print("❌ First load or create configuration")
            return

        match command:
            case "save":
                if not self.config:
                    print("❌ No configuration to save")
                    return
                if not api_name:
                    print("❌ Specify API name, e.g., 'setting save open-meteo'")
                    return
                if api_name not in self.apis:
                    print(f"❌ Unknown API: {api_name}. Available: {', '.join(self.apis.keys())}")
                    return
                try:
                    path = extra[0].split("/") if extra else [api_name]
                    self.setting.save(self.config, [api_name] + path)
                    logger.info(f"Configuration saved for {api_name} at path {path or 'default'}")
                    print(f"Configuration saved for {api_name}")
                except ConfigError as e:
                    logger.error(f"Error saving config: {e}")
                    print(f"❌ Error saving: {e}")

            case "load":
                if self.api:
                    print("❌ API instance exists, delete it first with 'down'")
                    return
                if not api_name:
                    print("❌ Specify API name, e.g., 'config load open-meteo'")
                    return
                if api_name not in self.apis:
                    print(f"❌ Unknown API: {api_name}. Available: {', '.join(self.apis.keys())}")
                    return

                config_class = self.apis[api_name]["config"]
                try:
                    path = extra[0].split("/") if extra else [api_name]
                    self.config = self.setting.fetch(config_class, path)
                    logger.info(f"Configuration loaded for {api_name} at path {path or 'default'}")
                    print(f"Configuration loaded for {api_name}")
                except ConfigError as e:
                    logger.error(f"Error loading config: {e}")
                    print(f"❌ Error: {e}, creating new config")
                    self.config = config_class()

            case "show":
                if not self.config:
                    print("❌ No configuration loaded")
                    return
                api_name = next((name for name, info in self.apis.items() if info["config"] == type(self.config)), "unknown")
                print(f"Configuration for {api_name}:")
                for field_name in self.config.__annotations__.keys():
                    field_value = getattr(self.config, field_name, "not found")
                    print(f"  {field_name}: {field_value or 'not set'}")
                logger.info(f"Displayed configuration for {api_name}")

            case "set":
                if not self.config:
                    print("❌ First load configuration")
                    return
                if len(params) < 2:
                    print("❌ Usage: setting set [param] [value]")
                    return

                param, value = params if len(params) == 2 else (params[0], None)

                if hasattr(self.config, param):
                    try:
                        annotation = self.config.__annotations__.get(param)
                        value = self.setting._cast_value(value, annotation)
                        setattr(self.config, param, value)
                        logger.info(f"Config parameter {param} set to {value}")
                        print(f"{param} = {value}")
                    except (ValueError, ConfigError) as e:
                        logger.error(f"Error setting {param}: {e}")
                        print(f"❌ Error setting {param}: {e}")
                else:
                    print(f"❌ Unknown parameter: {param}")

            case "reset":
                if self.api:
                    print("❌ API instance exists, delete it first with 'down'")
                    return
                self.config = None
                logger.info("Configuration reset")
                print("Configuration reset")

            case _:
                print("❌ Invalid command. Use: save, load, show, set, reset")

    def do_up(self, args):
        """Create API instance: up [api_name]"""
        if not self.config:
            print("❌ First load configuration")
            return
        parts = args.split(maxsplit=1)
        api_name = parts[0] if parts else None
        if not api_name:
            print("❌ Specify API name, e.g., 'up open-meteo'")
            return
        if api_name not in self.apis:
            print(f"❌ Unknown API: {api_name}. Available: {', '.join(self.apis.keys())}")
            return
        try:
            self.api = self.apis[api_name]["class"](asdict(self.config))
            logger.info(f"API instance created for {api_name}")
            print(f"API created for {api_name}")
        except ApiError as e:
            logger.error(f"Error creating API: {e}")
            print(f"❌ Error creating API: {e}")

    def do_down(self, args=""):
        """Remove API instance."""
        self.api = None
        print("API instance removed")

    def do_refresh(self, args=""):
        """Refresh API data."""
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
