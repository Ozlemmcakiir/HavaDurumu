from unittest.mock import Mock, patch

from weather_service import WeatherService


def test_get_weather_ankara_parametreleri():
    payload = {
        "current_weather": {"temperature": 12.4, "weathercode": 0},
        "hourly": {},
        "daily": {},
    }
    fake = Mock()
    fake.json.return_value = payload
    fake.raise_for_status = Mock()

    with patch("weather_service.requests.get", return_value=fake) as get:
        out = WeatherService().get_weather(39.92, 32.85)

    assert out == payload
    args, kwargs = get.call_args
    assert args[0] == WeatherService.FORECAST_URL
    assert kwargs["timeout"] == 10
    assert kwargs["params"]["latitude"] == 39.92
    assert kwargs["params"]["longitude"] == 32.85
    assert kwargs["params"]["current_weather"] == "true"
    assert "temperature_2m" in kwargs["params"]["hourly"]
    assert "temperature_2m_max" in kwargs["params"]["daily"]


def test_get_weather_http_hata_yukseltir():
    fake = Mock()
    fake.raise_for_status.side_effect = RuntimeError("http 500")

    with patch("weather_service.requests.get", return_value=fake):
        try:
            WeatherService().get_weather(0, 0)
            assert False, "hata bekleniyordu"
        except RuntimeError as exc:
            assert "http 500" in str(exc)
