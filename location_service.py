import requests


class LocationService:

    GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"

    def search_city(self, city_name):

        response = requests.get(
            self.GEOCODE_URL,
            params={
                "name": city_name,
                "count": 8,
                "language": "tr",
                "format": "json",
            },
            timeout=10,
        )

        response.raise_for_status()

        return response.json().get("results", [])