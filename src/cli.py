from loguru import logger
from ometeo import OpenMeteoAPI
import click


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
    try:
        api: OpenMeteoAPI = OpenMeteoAPI(
            city=city,
            country=country,
            language=language,
            count=count
        )
    except Exception as e:
        logger.error("Error creating API instance: {}", e)
        return

    api.refresh()
    print(api.get_endpoint("GeoEndpoint").data)
    logger.info("GeoEndpoint data: {}", api.get_endpoint("GeoEndpoint").data)

if __name__ == "__main__":
    cli()
