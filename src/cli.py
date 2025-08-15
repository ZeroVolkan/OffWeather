from loguru import logger
from dataclasses import dataclass
from setting import Setting
from ometeo import OpenMeteoAPI

import click

exist_apis = {
    "open-meteo",
}


@dataclass
class ConfigCLI:
    api_key: str | None = None
    city: str | None = None
    country: str | None = None
    language: str | None = None
    count: int | None = None


@click.group()
def cli():
    logger.add(".log/cli.log")
    logger.info("Starting CLI")


@cli.command()
@click.option("--api-key", default=None, help="API key for OpenMeteo")
@click.option("--city", default=None, help="City name")
@click.option("--country", default=None, help="Country name")
@click.option("--language", default=None, help="Language code")
@click.option("--count", default=None, type=int, help="Number of results")
def open_meteo(api_key, city, country, language, count):
    setting = Setting("setting.toml")

    try:
        config = setting.fetch(ConfigCLI, ["open-meteo"])
    except (KeyError, TypeError) as e:
        print(e)
        # Если конфигурация не найдена, создаем новую
        config = ConfigCLI()

    # Обновляем конфигурацию только теми параметрами, которые переданы
    if api_key is not None:
        config.api_key = api_key
    if city is not None:
        config.city = city
    if country is not None:
        config.country = country
    if language is not None:
        config.language = language
    if count is not None:
        config.count = count

    try:
        api: OpenMeteoAPI = OpenMeteoAPI(
            city=config.city,
            country=config.country,
            language=config.language,
            count=config.count
        )
    except Exception as e:
        logger.error("Error creating API instance: {}", e)
        return

    api.refresh()
    logger.info("GeoEndpoint data: {}", api.get_endpoint("GeoEndpoint").data)


@cli.command()
@click.option("--api")
@click.option("--api-key", default=None, help="API key for OpenMeteo")
@click.option("--city", default=None, help="City name")
@click.option("--country", default=None, help="Country name")
@click.option("--language", default=None, help="Language code")
@click.option("--count", default=None, type=int, help="Number of results")
def setting(api, api_key, city, country, language, count):
    if not api and api in exist_apis:
        logger.error("API key is required")
        return

    setting = Setting("setting.toml")

    # Создаем объект конфигурации
    config = ConfigCLI(
        api_key=api_key,
        city=city,
        country=country,
        language=language,
        count=count
    )

    # Сохраняем с помощью нового метода save
    setting.save(config, [api])
    logger.info("Configuration saved successfully")


if __name__ == "__main__":
    cli()
