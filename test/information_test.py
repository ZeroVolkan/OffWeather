from src.static import apis

def test_apis_function():
    from src.open_meteo.api import OpenMeteoAPI, OpenMeteoConfig
    """Test that apis function returns correct API information."""
    api_info = apis()
    assert "OpenMeteoAPI" in api_info
    assert api_info["OpenMeteoAPI"]["class"] == OpenMeteoAPI
    assert api_info["OpenMeteoAPI"]["config"] == OpenMeteoConfig


def test_apis_structure():
    """Test that APIs have correct structure."""
    api_info = apis()
    for api_name, api_data in api_info.items():
        assert "class" in api_data
        assert "config" in api_data


def test_open_meteo_api():
    """Test open_meteo API configuration."""
    from src.open_meteo.api import OpenMeteoAPI, OpenMeteoConfig
    api_info = apis()
    open_meteo = api_info["OpenMeteoAPI"]
    assert open_meteo["class"] == OpenMeteoAPI
    assert open_meteo["config"] == OpenMeteoConfig
