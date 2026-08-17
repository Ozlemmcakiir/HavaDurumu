import flet as ft

from weather_app import WeatherApp


def main(page: ft.Page):
    app = WeatherApp(page)
    app.start()


if __name__ == "__main__":
    ft.run(
        main,
        view=ft.AppView.WEB_BROWSER,
        assets_dir="assets",
    )
