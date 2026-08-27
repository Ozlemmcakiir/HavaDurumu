from datetime import datetime

import flet as ft

from location_service import LocationService
from weather_service import WeatherService
from weather_utils import WeatherTheme, WeatherUtils

DEFAULT_PLACE = {
    "name": "Ankara",
    "admin1": "Ankara",
    "country": "Türkiye",
    "latitude": 39.92,
    "longitude": 32.85,
}

DAY_NAMES = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]


class WeatherApp:
    """Sayfa orkestrasyonu: arama + hava kartları. Veri işi servislere aittir."""

    def __init__(self, page: ft.Page, location_service=None, weather_service=None):
        self.page = page
        self.location_service = location_service or LocationService()
        self.weather_service = weather_service or WeatherService()
        self._build_controls()

    def start(self):
        self._setup_page()
        self._mount()
        self.load_weather(DEFAULT_PLACE)

    def _setup_page(self):
        page = self.page
        page.title = "Gökyüzü — Hava Durumu"
        page.favicon = "logo.png"
        page.window.width = 460
        page.window.height = 780
        page.window.min_width = 380
        page.padding = 0
        page.bgcolor = WeatherTheme.BG_DARK
        page.fonts = {
            "Display": "https://raw.githubusercontent.com/google/fonts/main/ofl/spacegrotesk/SpaceGrotesk[wght].ttf",
        }
        page.theme = ft.Theme(font_family="Inter")

    def _build_controls(self):
        theme = WeatherTheme

        self.search_field = ft.TextField(
            hint_text="Şehir veya ülke ara — örn. İzmir, Tokyo, Cape Town",
            border_radius=14,
            border_color=theme.CARD_BORDER,
            focused_border_color=theme.AMBER,
            bgcolor=theme.CARD_BG,
            color=theme.TEXT,
            hint_style=ft.TextStyle(color=theme.MUTED),
            prefix_icon=ft.Icons.SEARCH_ROUNDED,
            height=52,
            content_padding=ft.Padding.symmetric(horizontal=14, vertical=8),
            on_change=self.run_search,
            on_submit=self.run_search,
        )

        self.suggestions_list = ft.Column(spacing=0, visible=False)
        self.suggestions_card = ft.Container(
            content=self.suggestions_list,
            bgcolor=theme.CARD_BG,
            border=ft.Border.all(1, theme.CARD_BORDER),
            border_radius=14,
            padding=4,
            visible=False,
        )

        self.city_name_txt = ft.Text(
            "", size=20, weight=ft.FontWeight.W_600, color=theme.TEXT, font_family="Display"
        )
        self.city_meta_txt = ft.Text("", size=13, color=theme.MUTED)
        self.coords_txt = ft.Text("", size=11, color=theme.MUTED, font_family="monospace")
        self.temp_txt = ft.Text(
            "--°", size=64, weight=ft.FontWeight.BOLD, color=theme.TEXT, font_family="Display"
        )
        self.desc_txt = ft.Text("—", size=15, color=theme.MUTED)
        self.main_icon = ft.Icon(ft.Icons.CLOUD_ROUNDED, size=84, color=theme.MUTED)

        self.wind_txt = ft.Text("--", size=15, color=theme.TEXT, font_family="monospace")
        self.humidity_txt = ft.Text("--", size=15, color=theme.TEXT, font_family="monospace")
        self.sun_txt = ft.Text("-- / --", size=12, color=theme.TEXT, font_family="monospace")

        self.metrics_row = ft.Row(
            [
                self._metric_box("Rüzgar", self.wind_txt, ft.Icons.AIR_ROUNDED),
                self._metric_box("Nem", self.humidity_txt, ft.Icons.WATER_DROP_OUTLINED),
                self._metric_box("Gündoğ./Batım", self.sun_txt, ft.Icons.WB_TWILIGHT),
            ],
            spacing=10,
        )

        self.main_panel = ft.Container(
            content=ft.Column(
                [
                    ft.Row([self.city_name_txt, self.city_meta_txt], spacing=8),
                    self.coords_txt,
                    ft.Row(
                        [
                            ft.Column([self.temp_txt, self.desc_txt], spacing=2),
                            self.main_icon,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    self.metrics_row,
                ],
                spacing=10,
            ),
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_LEFT,
                end=ft.Alignment.BOTTOM_RIGHT,
                colors=["#1c4d8f", "#4f9fc9"],
            ),
            border_radius=20,
            padding=22,
            animate=ft.Animation(600, ft.AnimationCurve.EASE_OUT),
        )

        self.loader = ft.Container(
            content=ft.ProgressRing(color=theme.AMBER, width=32, height=32),
            alignment=ft.Alignment.CENTER,
            padding=30,
            visible=False,
        )

        self.hourly_row = ft.Row(spacing=10, scroll=ft.ScrollMode.AUTO)
        self.hourly_section = ft.Column(
            [
                ft.Text("SONRAKİ 24 SAAT", size=12, color=theme.MUTED, weight=ft.FontWeight.W_600),
                self.hourly_row,
            ],
            spacing=8,
            visible=False,
        )

        self.daily_col = ft.Column(spacing=0)
        self.daily_section = ft.Column(
            [
                ft.Text("7 GÜNLÜK TAHMİN", size=12, color=theme.MUTED, weight=ft.FontWeight.W_600),
                ft.Container(
                    content=self.daily_col,
                    bgcolor=theme.CARD_BG,
                    border=ft.Border.all(1, theme.CARD_BORDER),
                    border_radius=16,
                    padding=6,
                ),
            ],
            spacing=8,
            visible=False,
        )

    def _metric_box(self, label, value_control, icon):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        label.upper(),
                        size=10,
                        color=WeatherTheme.MUTED,
                        weight=ft.FontWeight.W_500,
                    ),
                    ft.Row(
                        [ft.Icon(icon, size=14, color=WeatherTheme.AMBER), value_control],
                        spacing=6,
                    ),
                ],
                spacing=4,
            ),
            bgcolor=WeatherTheme.METRIC_BG,
            border=ft.Border.all(1, WeatherTheme.METRIC_BORDER),
            border_radius=12,
            padding=10,
            expand=True,
        )

    def _mount(self):
        header_row = ft.Row(
            [
                ft.Image(src="logo.png", width=32, height=32),
                ft.Text(
                    " BGTS ",
                    size=24,
                    weight=ft.FontWeight.W_900,
                    color=WeatherTheme.TEXT,
                    font_family="Display",
                ),
                ft.Text(
                    " DevOps SRE",
                    size=15,
                    weight=ft.FontWeight.W_800,
                    color=WeatherTheme.MUTED,
                ),
            ],
            spacing=0,
            tight=True,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self.page.add(
            ft.Container(
                content=ft.Column(
                    [
                        header_row,
                        self.search_field,
                        self.suggestions_card,
                        self.loader,
                        self.main_panel,
                        self.hourly_section,
                        self.daily_section,
                        ft.Text(
                            "Veri kaynağı: Open-Meteo",
                            size=11,
                            color=WeatherTheme.MUTED,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    spacing=18,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=20,
                expand=True,
            )
        )

    def run_search(self, e):
        query = (self.search_field.value or "").strip()
        if len(query) < 2:
            self.suggestions_card.visible = False
            self.page.update()
            return

        try:
            results = self.location_service.search_city(query)
        except Exception:
            results = []

        self.render_suggestions(results)

    def render_suggestions(self, results):
        self.suggestions_list.controls.clear()
        if not results:
            self.suggestions_list.controls.append(
                ft.Container(
                    ft.Text("Sonuç bulunamadı.", color=WeatherTheme.MUTED, size=13),
                    padding=12,
                )
            )
        else:
            for place in results:
                meta = ", ".join(p for p in [place.get("admin1"), place.get("country")] if p)
                self.suggestions_list.controls.append(
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Text(place["name"], color=WeatherTheme.TEXT, size=14),
                                ft.Text(meta, color=WeatherTheme.MUTED, size=12),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        padding=ft.Padding.symmetric(horizontal=12, vertical=10),
                        border_radius=10,
                        ink=True,
                        on_click=lambda e, selected=place: self.select_place(selected),
                    )
                )

        self.suggestions_card.visible = True
        self.suggestions_list.visible = True
        self.page.update()

    def select_place(self, place):
        self.search_field.value = f"{place['name']}, {place.get('country', '')}"
        self.suggestions_card.visible = False
        self.page.update()
        self.load_weather(place)

    def load_weather(self, place):
        self.loader.visible = True
        self.main_panel.visible = False
        self.hourly_section.visible = False
        self.daily_section.visible = False
        self.page.update()

        try:
            data = self.weather_service.get_weather(place["latitude"], place["longitude"])
        except Exception as ex:
            self.loader.visible = False
            self.page.show_dialog(ft.SnackBar(ft.Text(f"Hava durumu alınamadı: {ex}")))
            self.page.update()
            return

        self.render_weather(place, data)
        self.loader.visible = False
        self.main_panel.visible = True
        self.hourly_section.visible = True
        self.daily_section.visible = True
        self.page.update()

    def render_weather(self, place, data):
        current = data["current_weather"]
        is_day = current.get("is_day", 1) == 1
        icon, icon_color = WeatherUtils.get_icon(current["weathercode"], is_day)

        self.city_name_txt.value = place["name"]
        self.city_meta_txt.value = ", ".join(
            p for p in [place.get("admin1"), place.get("country")] if p
        )
        self.coords_txt.value = (
            f"{place['latitude']:.2f}°, {place['longitude']:.2f}°  ·  {data.get('timezone', '')}"
        )
        self.temp_txt.value = f"{round(current['temperature'])}°"
        self.desc_txt.value = WeatherUtils.get_description(current["weathercode"])
        self.main_icon.name = icon
        self.main_icon.color = icon_color
        self.main_panel.gradient = ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT,
            end=ft.Alignment.BOTTOM_RIGHT,
            colors=WeatherUtils.get_gradient(is_day, current["weathercode"]),
        )
        self.wind_txt.value = f"{round(current['windspeed'])} km/s"

        now = datetime.now()
        hourly_times = [datetime.fromisoformat(t) for t in data["hourly"]["time"]]
        closest_idx = min(range(len(hourly_times)), key=lambda i: abs(hourly_times[i] - now))
        self.humidity_txt.value = f"{data['hourly']['relative_humidity_2m'][closest_idx]}%"

        sunrise = datetime.fromisoformat(data["daily"]["sunrise"][0]).strftime("%H:%M")
        sunset = datetime.fromisoformat(data["daily"]["sunset"][0]).strftime("%H:%M")
        self.sun_txt.value = f"{sunrise} / {sunset}"

        self._render_hourly(data, hourly_times, now)
        self._render_daily(data)

    def _render_hourly(self, data, hourly_times, now):
        self.hourly_row.controls.clear()
        start_idx = next((i for i, t in enumerate(hourly_times) if t >= now), 0)
        hourly = data["hourly"]

        for i in range(start_idx, min(start_idx + 24, len(hourly_times))):
            h_icon, h_color = WeatherUtils.get_icon(
                hourly["weathercode"][i],
                6 <= hourly_times[i].hour < 20,
            )
            self.hourly_row.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "Şimdi" if i == start_idx else hourly_times[i].strftime("%H:%M"),
                                size=11,
                                color=WeatherTheme.MUTED,
                                font_family="monospace",
                            ),
                            ft.Icon(h_icon, size=22, color=h_color),
                            ft.Text(
                                f"{round(hourly['temperature_2m'][i])}°",
                                size=14,
                                weight=ft.FontWeight.W_600,
                                color=WeatherTheme.TEXT,
                            ),
                        ],
                        spacing=6,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    bgcolor=WeatherTheme.CARD_BG,
                    border=ft.Border.all(1, WeatherTheme.CARD_BORDER),
                    border_radius=14,
                    padding=ft.Padding.symmetric(vertical=12, horizontal=6),
                    width=64,
                )
            )

    def _render_daily(self, data):
        self.daily_col.controls.clear()
        daily = data["daily"]
        all_temps = daily["temperature_2m_max"] + daily["temperature_2m_min"]
        tmax, tmin = max(all_temps), min(all_temps)
        span = (tmax - tmin) or 1

        for i, t in enumerate(daily["time"]):
            day = datetime.fromisoformat(t)
            label = "Bugün" if i == 0 else DAY_NAMES[day.weekday()]
            d_icon, d_color = WeatherUtils.get_icon(daily["weathercode"][i], True)
            lo, hi = daily["temperature_2m_min"][i], daily["temperature_2m_max"][i]
            left_pct = (lo - tmin) / span
            width_pct = (hi - lo) / span

            self.daily_col.controls.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Container(ft.Text(label, size=13, color=WeatherTheme.TEXT), width=70),
                            ft.Icon(d_icon, size=20, color=d_color),
                            ft.Container(
                                ft.Text(
                                    f"{round(lo)}°",
                                    size=12,
                                    color=WeatherTheme.MUTED,
                                    font_family="monospace",
                                ),
                                width=32,
                                alignment=ft.Alignment.CENTER,
                            ),
                            ft.Container(
                                content=ft.Stack(
                                    [
                                        ft.Container(
                                            bgcolor=WeatherTheme.BAR_TRACK,
                                            border_radius=3,
                                            height=4,
                                            expand=True,
                                        ),
                                        ft.Container(
                                            bgcolor=WeatherTheme.AMBER,
                                            border_radius=3,
                                            height=4,
                                            margin=ft.Margin.only(left=left_pct * 140),
                                            width=max(width_pct * 140, 6),
                                        ),
                                    ]
                                ),
                                width=140,
                            ),
                            ft.Container(
                                ft.Text(
                                    f"{round(hi)}°",
                                    size=12,
                                    color=WeatherTheme.TEXT,
                                    font_family="monospace",
                                ),
                                width=32,
                                alignment=ft.Alignment.CENTER,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=ft.Padding.symmetric(vertical=10, horizontal=8),
                    border=(
                        ft.Border.only(bottom=ft.BorderSide(1, WeatherTheme.ROW_DIVIDER))
                        if i < len(daily["time"]) - 1
                        else None
                    ),
                )
            )