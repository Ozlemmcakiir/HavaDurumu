import flet as ft


class WeatherApp:

    def __init__(self, page: ft.Page):
        self.page = page

    def start(self):
        self.setup_page()

        self.page.add(
            ft.Text(
                "Gökyüzü — Hava Durumu",
                size=24,
            )
        )

    def setup_page(self):
        self.page.title = "Gökyüzü — Hava Durumu"
        self.page.assets_dir = "assets"
        self.page.favicon = "logo.png"

        self.page.window.width = 460
        self.page.window.height = 780
        self.page.window.min_width = 380

        self.page.padding = 0
        self.page.bgcolor = "#0B1220"