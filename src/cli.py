import cmd
import click
from loguru import logger
from dataclasses import dataclass
from setting import Setting
from open_meteo.api import OpenMeteoAPI

exist_apis = {
    "open-meteo": {
        "class": "OpenMeteoAPI",
        "config": "OpenMeteoConfig",
    },
    # Можно добавить другие API здесь
    # "weather-api": {
    #     "class": "WeatherAPI",
    #     "config": "WeatherConfig",
    # },
}


@dataclass
class OpenMeteoConfig:
    api_key: str | None = None
    city: str | None = None
    country: str | None = None
    language: str | None = None
    count: int | None = None


class DebugShell(cmd.Cmd):
    prompt = "(debug) "
    intro = "Debug Shell - введите help для справки"

    def __init__(self):
        super().__init__()
        self.setting = Setting("setting.toml")
        self.config = None
        self.api = None
        self.current_api = None
        self.current_config_class = None
        logger.add(".log/debug.log")
        logger.info("Debug shell started")

    def do_list(self, args):
        """Показать доступные API"""
        print("Avalible apis:")
        for api_name, api_info in exist_apis.items():
            status = "Active" if api_name == self.current_api else "⚫ Avalible"
            print(f"  {api_name} ({api_info['class']}) - {status}")

    def do_api(self, api_name):
        """Setting to API: api open-meteo"""
        if not api_name or api_name not in exist_apis:
            print(f"❌ Avalible apis: {list(exist_apis)}")
            return

        self.current_api = api_name
        self.current_config_class = self._get_config_class(api_name)
        logger.info(f"Setting to API: {api_name}")
        print(f"Setting to {api_name}")

        # Загружаем конфигурацию для этого API
        try:
            self.config = self.setting.fetch(self.current_config_class, [api_name])
            logger.info(f"Config loaded for {api_name}")
            print("Config loaded")
        except Exception as e:
            logger.warning(f"Config not found for {api_name}: {e}")
            print("Config not found, created new")
            self.config = self.current_config_class()

    def _get_config_class(self, api_name):
        """Get config class for API"""
        if api_name not in exist_apis:
            return OpenMeteoConfig

        api_info = exist_apis[api_name]
        if api_info["config"] == "OpenMeteoConfig":
            return OpenMeteoConfig
        else:
            # Для будущих API добавить здесь другие классы TEMP
            return OpenMeteoConfig

    def do_config(self, api_name):
        """Loading configuration: config open-meteo"""
        if not api_name:
            api_name = self.current_api
        if not api_name:
            print("❌ Choice API, use api")
            return

        config_class = self._get_config_class(api_name)

        try:
            self.config = self.setting.fetch(config_class, [api_name])
            self.current_config_class = config_class
            logger.info(f"Config loaded for {api_name}")
            print("Configuration loaded")
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            print(f"❌ Error: {e}")
            self.config = config_class()
            self.current_config_class = config_class

    def do_up(self, args):
        """Create API instance"""
        if not self.config:
            print("❌ First load configuration")
            return

        if not self.current_api:
            print("❌ First switch to API")
            return

        try:
            if self.current_api == "open-meteo":
                self.api = OpenMeteoAPI(
                    city=self.config.city,
                    country=self.config.country,
                    language=self.config.language,
                    count=self.config.count,
                )
            # Here you can add other APIs

            logger.info(f"API instance created for {self.current_api}")
            print("API created")
        except Exception as e:
            logger.error(f"Error creating API: {e}")
            print(f"❌ Error creating API: {e}")

    def do_refresh(self, args):
        """Refresh API"""
        if not self.api:
            print("❌ First create API")
            return

        try:
            self.api.refresh()
            logger.info("API data refreshed")
            print("Data refreshed")
        except Exception as e:
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
        except Exception as e:
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
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            print(f"❌ Error saving: {e}")

    def do_status(self, args):
        """Show detailed status"""
        print("Status: ")
        print(f"  Current API: {self.current_api or 'not selected'}")
        if self.current_api and self.current_api in exist_apis:
            api_info = exist_apis[self.current_api]
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

        print(f"  Avaliable API: {len(exist_apis)} ({', '.join(exist_apis.keys())})")

    def do_quit(self, args):
        """Exit"""
        logger.info("Debug shell stopped")
        return True

    def do_q(self, args):
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



@click.group()
def cli():
    logger.add(".log/cli.log")
    logger.info("Starting CLI")


@cli.command()
def debug():
    """Run debug shell"""
    DebugShell().cmdloop()


@cli.command()
@click.option("--api-key", default=None, help="API key for OpenMeteo")
@click.option("--city", default=None, help="City name")
@click.option("--country", default=None, help="Country name")
@click.option("--language", default=None, help="Language code")
@click.option("--count", default=None, type=int, help="Number of results")
def open_meteo(api_key, city, country, language, count):
    setting = Setting("setting.toml")

    try:
        config = setting.fetch(OpenMeteoConfig, ["open-meteo"])
    except (KeyError, TypeError):
        config = OpenMeteoConfig()

    try:
        api: OpenMeteoAPI = OpenMeteoAPI(
            city=config.city or city,
            country=config.country or country,
            language=config.language or language,
            count=config.count or count,
        )
    except Exception as e:
        logger.error("Error creating API instance: {}", e)
        return

    api.refresh()
    logger.info("GeoEndpoint data: {}", api.get_endpoint("GeoEndpoint").data)


@cli.command()
@click.option("--api", required=True)
@click.option("--api-key", default=None, help="API key for OpenMeteo")
@click.option("--city", default=None, help="City name")
@click.option("--country", default=None, help="Country name")
@click.option("--language", default=None, help="Language code")
@click.option("--count", default=None, type=int, help="Number of results")
def setting(api, api_key, city, country, language, count):
    if api not in exist_apis:
        logger.error("API doesn't exist")
        return

    setting = Setting("setting.toml")

    # Определяем класс конфигурации
    config_class = _get_config_class_by_name(api)

    config = config_class(
        api_key=api_key, city=city, country=country, language=language, count=count
    )
    setting.save(config, [api])
    logger.info("Configuration saved successfully")


def _get_config_class_by_name(api_name):
    """Вспомогательная функция для получения класса конфигурации"""
    if api_name not in exist_apis:
        return OpenMeteoConfig

    api_info = exist_apis[api_name]
    if api_info["config"] == "OpenMeteoConfig":
        return OpenMeteoConfig
    else:
        return OpenMeteoConfig


if __name__ == "__main__":
    cli()
