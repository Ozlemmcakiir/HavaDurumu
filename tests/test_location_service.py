from unittest.mock import Mock, patch

from location_service import LocationService


def test_search_city_sonuclari_doner():
    payload = {
        "results": [
            {"name": "Ankara", "country": "Türkiye", "latitude": 39.92, "longitude": 32.85}
        ]
    }
    fake = Mock()
    fake.json.return_value = payload
    fake.raise_for_status = Mock()

    with patch("location_service.requests.get", return_value=fake) as get:
        out = LocationService().search_city("Ankara")

    assert len(out) == 1
    assert out[0]["name"] == "Ankara"
    args, kwargs = get.call_args
    assert args[0] == LocationService.GEOCODE_URL
    assert kwargs["params"]["name"] == "Ankara"
    assert kwargs["params"]["language"] == "tr"
    assert kwargs["params"]["count"] == 8
    assert kwargs["timeout"] == 10


def test_search_city_bos_sonuc():
    fake = Mock()
    fake.json.return_value = {}
    fake.raise_for_status = Mock()

    with patch("location_service.requests.get", return_value=fake):
        assert LocationService().search_city("xyzxyzxyz") == []
