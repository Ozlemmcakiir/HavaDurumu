import os
import flet as ft
from weather_app import WeatherApp


def main(page: ft.Page):
    app = WeatherApp(page)
    app.start()


if __name__ == "__main__":
    # Host varsayılanı '0.0.0.0', Port varsayılanı '8080' yapıldı
    host = os.getenv("FLET_SERVER_IP") or os.getenv("FLET_HOST") or "0.0.0.0"
    port_raw = os.getenv("FLET_SERVER_PORT") or os.getenv("FLET_PORT") or "8080"
    
    try:
        port = int(port_raw)
    except ValueError:
        port = 8080

    ft.run(
        main,
        view=ft.AppView.WEB_BROWSER,
        assets_dir="assets",
        host=host,
        port=port,
    )