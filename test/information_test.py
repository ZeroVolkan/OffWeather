import pytest

from src.information import Information
from src.open_meteo.api import OpenMeteoAPI, OpenMeteoConfig


def test_singleton():
    """Test that Information class is a singleton."""
    info1 = Information()
    info2 = Information()
    assert info1 is info2


def test_get_api():
    """Test loading API via attribute."""
    info = Information()
    api = info.open_meteo
    assert api["class"] == OpenMeteoAPI
    assert api["config"] == OpenMeteoConfig


def test_cached_api():
    """Test that API is cached after first load."""
    info = Information()
    api1 = info.open_meteo
    api2 = info.open_meteo
    assert api1 is api2


def test_missing_api():
    """Test error handling for missing API."""
    info = Information()
    with pytest.raises(AttributeError, match="API unknown_api not found"):
        info.unknown_api


def test_import_error():
    from src.information import apis

    # Test don't change global statement
    apis["unknown_api"] = {
        "module": "src.unknown_api.api",
        "class": "UnknownAPI",
        "config": "UnknownConfig",
    }

    info = Information()

    with pytest.raises(RuntimeError, match="Error loading API unknown_api"):
        info.unknown_api

    # For safety
    apis.pop("unknown_api")
