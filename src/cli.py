import cmd
import click
from loguru import logger
from dataclasses import dataclass
from setting import Setting
from ometeo import OpenMeteoAPI

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

    def do_list_apis(self, args):
        """Показать доступные API"""
        print("🌍 Доступные API:")
        for api_name, api_info in exist_apis.items():
            status = "✅ активен" if api_name == self.current_api else "⚫ доступен"
            print(f"  {api_name} ({api_info['class']}) - {status}")

    def do_switch_api(self, api_name):
        """Переключиться на API: switch_api open-meteo"""
        if not api_name or api_name not in exist_apis:
            print(f"❌ Доступные API: {list(exist_apis)}")
            return

        self.current_api = api_name
        self.current_config_class = self._get_config_class(api_name)
        logger.info(f"Switched to API: {api_name}")
        print(f"🔄 Переключено на {api_name}")

        # Загружаем конфигурацию для этого API
        try:
            self.config = self.setting.fetch(self.current_config_class, [api_name])
            logger.info(f"Config loaded for {api_name}")
            print(f"✅ Конфигурация загружена")
        except Exception as e:
            logger.warning(f"Config not found for {api_name}: {e}")
            print(f"⚠️ Конфигурация не найдена, создана новая")
            self.config = self.current_config_class()

    def _get_config_class(self, api_name):
        """Получить класс конфигурации для API"""
        if api_name not in exist_apis:
            return OpenMeteoConfig

        api_info = exist_apis[api_name]
        if api_info["config"] == "OpenMeteoConfig":
            return OpenMeteoConfig
        else:
            # Для будущих API добавить здесь другие классы
            return OpenMeteoConfig

    def do_load_config(self, api_name):
        """Загрузить конфигурацию: load_config open-meteo"""
        if not api_name:
            api_name = self.current_api
        if not api_name:
            print("❌ Укажите API или используйте switch_api")
            return

        config_class = self._get_config_class(api_name)

        try:
            self.config = self.setting.fetch(config_class, [api_name])
            self.current_config_class = config_class
            logger.info(f"Config loaded for {api_name}")
            print(f"✅ Конфигурация загружена")
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            print(f"❌ Ошибка: {e}")
            self.config = config_class()
            self.current_config_class = config_class

    def do_create_api(self, args):
        """Создать API экземпляр"""
        if not self.config:
            print("❌ Сначала загрузите конфигурацию")
            return

        if not self.current_api:
            print("❌ Сначала переключитесь на API")
            return

        try:
            if self.current_api == "open-meteo":
                self.api = OpenMeteoAPI(
                    city=self.config.city,
                    country=self.config.country,
                    language=self.config.language,
                    count=self.config.count,
                )
            # Здесь можно добавить другие API

            logger.info(f"API instance created for {self.current_api}")
            print("✅ API создан")
        except Exception as e:
            logger.error(f"Error creating API: {e}")
            print(f"❌ Ошибка создания API: {e}")

    def do_refresh(self, args):
        """Обновить данные API"""
        if not self.api:
            print("❌ Сначала создайте API")
            return

        try:
            self.api.refresh()
            logger.info("API data refreshed")
            print("✅ Данные обновлены")
        except Exception as e:
            logger.error(f"Error refreshing API: {e}")
            print(f"❌ Ошибка: {e}")

    def do_show_data(self, endpoint):
        """Показать данные: show_data GeoEndpoint"""
        if not self.api:
            print("❌ Сначала создайте API")
            return

        try:
            data = self.api.get_endpoint(endpoint or "GeoEndpoint").data
            logger.info(f"Data retrieved from {endpoint}")
            print(f"📊 Данные {endpoint}: {data}")
        except Exception as e:
            logger.error(f"Error getting data from {endpoint}: {e}")
            print(f"❌ Ошибка: {e}")

    def do_set_config(self, args):
        """Изменить параметр конфигурации: set_config city Moscow"""
        if not self.config:
            print("❌ Сначала загрузите конфигурацию")
            return

        parts = args.split(maxsplit=1)
        if len(parts) < 2:
            print("❌ Использование: set_config <параметр> <значение>")
            return

        param, value = parts
        if value.lower() == "none":
            value = None
        elif param == "count" and value is not None:
            try:
                value = int(value)
            except ValueError:
                print(f"❌ Неверное значение для count: {value}")
                return

        if hasattr(self.config, param):
            setattr(self.config, param, value)
            logger.info(f"Config parameter {param} set to {value}")
            print(f"✅ {param} = {value}")
        else:
            print(f"❌ Неизвестный параметр: {param}")

    def do_save_config(self, args):
        """Сохранить конфигурацию"""
        if not self.config:
            print("❌ Нет конфигурации для сохранения")
            return

        if not self.current_api:
            print("❌ Не выбрано API")
            return

        try:
            self.setting.save(self.config, [self.current_api])
            logger.info(f"Config saved for {self.current_api}")
            print(f"✅ Конфигурация сохранена для {self.current_api}")
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            print(f"❌ Ошибка сохранения: {e}")

    def do_status(self, args):
        """Показать детальный статус"""
        print("📊 Статус системы:")
        print(f"  Текущий API: {self.current_api or 'не выбран'}")
        if self.current_api and self.current_api in exist_apis:
            api_info = exist_apis[self.current_api]
            print(f"    Класс API: {api_info['class']}")
            print(f"    Конфиг: {api_info['config']}")

        print(f"  Конфигурация: {'загружена' if self.config else 'не загружена'}")
        if self.config:
            print(
                f"    Тип конфига: {self.current_config_class.__name__ if self.current_config_class else 'unknown'}"
            )
            for field_name in self.config.__annotations__.keys():
                field_value = getattr(self.config, field_name, "не найдено")
                if field_name == "api_key" and field_value:
                    field_value = "***скрыт***"
                print(f"    {field_name}: {field_value or 'не установлен'}")

        print(f"  API экземпляр: {'создан' if self.api else 'не создан'}")
        if self.api:
            print(
                f"    Endpoints: {list(self.api.endpoints.keys()) if hasattr(self.api, 'endpoints') else 'н/д'}"
            )

        print(f"  Доступные API: {len(exist_apis)} ({', '.join(exist_apis.keys())})")

    def do_quit(self, args):
        """Выход"""
        logger.info("Debug shell stopped")
        return True


@click.group()
def cli():
    logger.add(".log/cli.log")
    logger.info("Starting CLI")


@cli.command()
def debug():
    """Запустить debug shell"""
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
