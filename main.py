import os

import flet as ft

from weather_app import WeatherApp


def main(page: ft.Page):
    app = WeatherApp(page)
    app.start()


if __name__ == "__main__":
    host = os.getenv("FLET_SERVER_IP") or os.getenv("FLET_HOST") or None
    port_raw = os.getenv("FLET_SERVER_PORT") or os.getenv("FLET_PORT") or "0"
    port = int(port_raw)

    ft.run(
        main,
        view=ft.AppView.WEB_BROWSER,
        assets_dir="assets",
        host=host,
        port=port,
    )
