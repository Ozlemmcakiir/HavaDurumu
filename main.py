import os

import flet as ft

from weather_app import WeatherApp


def main(page: ft.Page):
    app = WeatherApp(page)
    app.start()


if __name__ == "__main__":
    host = os.getenv("FLET_HOST") or None
    port = int(os.getenv("FLET_PORT", "0"))

    ft.run(
        main,
        view=ft.AppView.WEB_BROWSER,
        assets_dir="assets",
        host=host,
        port=port,
    )
