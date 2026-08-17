import requests


class WeatherService:

    FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

    def get_weather(self, latitude, longitude):

        response = requests.get(
            self.FORECAST_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current_weather": "true",
                "hourly": "temperature_2m,relative_humidity_2m,weathercode,windspeed_10m",
                "daily": (
                    "weathercode,"
                    "temperature_2m_max,"
                    "temperature_2m_min,"
                    "sunrise,"
                    "sunset"
                ),
                "timezone": "auto",
            },
            timeout=10,
        )

        response.raise_for_status()

        return response.json()