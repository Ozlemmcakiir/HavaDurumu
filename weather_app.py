from datetime import datetime
import flet as ft
from location_service import LocationService
from weather_service import WeatherService
from weather_utils import WeatherUtils


class WeatherApp:

    def __init__(self, page: ft.Page):
        self.page = page
        self.location_service = LocationService()
        self.weather_service = WeatherService()

        # Arama Giriş Alanı
        self.city_input = ft.TextField(
            hint_text="Şehir veya ülke ara — örn. İzmi...",
            border_radius=10,
            border_color="#2A3B5C",
            focused_border_color="#4F9FC9",
            color="white",
            hint_style=ft.TextStyle(color="#8A99AD"),
            prefix_icon=ft.Icons.SEARCH,
            content_padding=12,
            expand=True,
            on_submit=self.on_search_click,
        )

        self.results_list = ft.ListView(
            spacing=5,
            padding=5,
            height=120,
            visible=False,
        )

        # Ana İçerik Konteyneri
        self.main_content = ft.Column(spacing=20, scroll=ft.ScrollMode.AUTO)

    def start(self):
        self.setup_page()

        self.page.add(
            ft.Column(
                controls=[
                    # Sol Üst Logo
                    ft.Row(
                        controls=[
                            ft.Image(src="logo.png", width=36, height=36, fit="contain")
                        ]
                    ),
                    # Arama Çubuğu
                    self.city_input,
                    self.results_list,
                    # Ana Sayfa İçeriği
                    self.main_content,
                ],
                spacing=15,
            )
        )

        # Uygulama açılır açılmaz varsayılan olarak Ankara'yı yükle
        self.load_weather_data("Ankara", "Ankara, Türkiye", 39.92, 32.85)

    def setup_page(self):
        self.page.title = "Gökyüzü — Hava Durumu"
        self.page.favicon = "logo.png"

        self.page.window.width = 460
        self.page.window.height = 800
        self.page.window.min_width = 380

        self.page.padding = 20
        self.page.bgcolor = "#0B1220"

    def on_search_click(self, e):
        query = self.city_input.value.strip()
        if not query:
            return

        try:
            cities = self.location_service.search_city(query)
            self.results_list.controls.clear()

            if not cities:
                self.results_list.controls.append(
                    ft.Text("Şehir bulunamadı.", color="red")
                )
            else:
                for city in cities:
                    name = city.get("name")
                    country = city.get("country", "")
                    admin1 = city.get("admin1", "")
                    lat = city.get("latitude")
                    lon = city.get("longitude")

                    location_sub = f"{admin1}, {country}".strip(", ")

                    self.results_list.controls.append(
                        ft.ListTile(
                            title=ft.Text(name, color="white"),
                            subtitle=ft.Text(location_sub, color="white54"),
                            on_click=lambda e, c_name=name, c_sub=location_sub, l1=lat, l2=lon: self.select_city(
                                c_name, c_sub, l1, l2
                            ),
                        )
                    )

            self.results_list.visible = True
            self.page.update()

        except Exception as err:
            print("Arama hatası:", err)

    def select_city(self, city_name, location_sub, lat, lon):
        self.results_list.visible = False
        self.load_weather_data(city_name, location_sub, lat, lon)

    def load_weather_data(self, city_name, location_sub, lat, lon):
        try:
            data = self.weather_service.get_weather(lat, lon)
            current = data.get("current_weather", {})
            daily = data.get("daily", {})
            hourly = data.get("hourly", {})

            temp = round(current.get("temperature", 0))
            code = current.get("weathercode", 0)
            wind = current.get("windspeed", 0)
            is_day = current.get("is_day", 1) == 1

            desc = WeatherUtils.get_description(code)
            icon_name = WeatherUtils.get_icon(code, is_day)
            grad_colors = WeatherUtils.get_gradient(is_day, code)

            # Nem, Gün Doğumu / Batımı Güvenli Çekim
            humidity_list = hourly.get("relative_humidity_2m", [0])
            humidity = humidity_list[0] if humidity_list else 0

            sunrise_list = daily.get("sunrise", ["--T--"])
            sunrise = sunrise_list[0].split("T")[-1][:5] if sunrise_list else "--:--"

            sunset_list = daily.get("sunset", ["--T--"])
            sunset = sunset_list[0].split("T")[-1][:5] if sunset_list else "--:--"

            # 1. ANA KART
            main_card = ft.Container(
                padding=20,
                border_radius=20,
                gradient=ft.LinearGradient(
                    begin=ft.Alignment(0, -1),
                    end=ft.Alignment(0, 1),
                    colors=grad_colors,
                ),
                content=ft.Column(
                    controls=[
                        ft.Text(city_name, size=24, weight=ft.FontWeight.BOLD, color="white"),
                        ft.Text(location_sub, size=12, color="white70"),
                        ft.Text(f"{lat}°, {lon}° · Europe/Istanbul", size=10, color="white54"),
                        ft.Container(height=10),
                        ft.Row(
                            controls=[
                                ft.Text(f"{temp}°", size=60, weight=ft.FontWeight.BOLD, color="white"),
                                ft.Icon(icon_name, size=65, color="white"),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Text(desc, size=16, color="white"),
                        ft.Container(height=10),
                        ft.Row(
                            controls=[
                                self._build_info_box("RÜZGAR", f"{wind} km/s", ft.Icons.AIR),
                                self._build_info_box("NEM", f"%{humidity}", ft.Icons.WATER_DROP),
                                self._build_info_box("GÜNDOĞ./BATIM", f"{sunrise} / {sunset}", ft.Icons.WB_SUNNY),
                            ],
                            spacing=10,
                        ),
                    ]
                ),
            )

            # 2. SONRAKİ 24 SAAT (Yatay Kaydırma)
            hourly_controls = []
            times = hourly.get("time", [])
            temps = hourly.get("temperature_2m", [])
            codes = hourly.get("weathercode", [])

            for i in range(min(12, len(times))):
                t_str = times[i].split("T")[-1][:5]
                h_temp = round(temps[i])
                h_code = codes[i]
                h_icon = WeatherUtils.get_icon(h_code, True)

                hourly_controls.append(
                    ft.Container(
                        padding=10,
                        width=65,
                        border_radius=12,
                        border=ft.border.all(1, "#2A3B5C"),
                        bgcolor="#0F172A",
                        content=ft.Column(
                            controls=[
                                ft.Text("Şimdi" if i == 0 else t_str, size=11, color="white70"),
                                ft.Icon(h_icon, size=20, color="white"),
                                ft.Text(f"{h_temp}°", size=14, weight=ft.FontWeight.BOLD, color="white"),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=6,
                        ),
                    )
                )

            hourly_section = ft.Column(
                controls=[
                    ft.Text("SONRAKİ 24 SAAT", size=12, weight=ft.FontWeight.BOLD, color="white54"),
                    ft.Row(controls=hourly_controls, scroll=ft.ScrollMode.ALWAYS),
                ]
            )

            # 3. 7 GÜNLÜK TAHMİN LİSTESİ
            days_controls = []
            days_time = daily.get("time", [])
            max_temps = daily.get("temperature_2m_max", [])
            min_temps = daily.get("temperature_2m_min", [])
            daily_codes = daily.get("weathercode", [])

            days_map = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]

            for i in range(len(days_time)):
                try:
                    d_date = datetime.strptime(days_time[i], "%Y-%m-%d")
                    day_name = "Bugün" if i == 0 else days_map[d_date.weekday()]
                except Exception:
                    day_name = f"{i+1}. Gün"

                d_min = round(min_temps[i]) if i < len(min_temps) else "--"
                d_max = round(max_temps[i]) if i < len(max_temps) else "--"
                d_code = daily_codes[i] if i < len(daily_codes) else 0
                d_icon = WeatherUtils.get_icon(d_code, True)

                days_controls.append(
                    ft.Row(
                        controls=[
                            ft.Text(day_name, size=14, color="white", width=60),
                            ft.Icon(d_icon, size=20, color="white"),
                            ft.Text(f"{d_min}°", size=14, color="white54", width=35, text_align=ft.TextAlign.RIGHT),
                            ft.Container(
                                expand=True,
                                height=4,
                                border_radius=2,
                                bgcolor="#1E293B",
                                content=ft.Container(bgcolor="#F97316", border_radius=2),
                            ),
                            ft.Text(f"{d_max}°", size=14, weight=ft.FontWeight.BOLD, color="white", width=35, text_align=ft.TextAlign.RIGHT),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    )
                )

            daily_section = ft.Container(
                padding=15,
                border_radius=15,
                border=ft.border.all(1, "#2A3B5C"),
                bgcolor="#0F172A",
                content=ft.Column(
                    controls=[
                        ft.Text("7 GÜNLÜK TAHMİN", size=12, weight=ft.FontWeight.BOLD, color="white54"),
                        ft.Divider(color="white12", height=10),
                        *days_controls,
                    ],
                    spacing=12,
                ),
            )

            # Ekrana Tüm Bölümleri Yerleştir
            self.main_content.controls = [main_card, hourly_section, daily_section]
            self.page.update()

        except Exception as err:
            print("Yükleme sırasında hata oluştu:", err)

    def _build_info_box(self, title, value, icon):
        return ft.Container(
            expand=True,
            padding=8,
            border_radius=10,
            bgcolor="#0F172A",
            content=ft.Column(
                controls=[
                    ft.Text(title, size=8, color="white54", weight=ft.FontWeight.BOLD),
                    ft.Row(
                        controls=[
                            ft.Icon(icon, size=14, color="white70"),
                            ft.Text(value, size=11, weight=ft.FontWeight.BOLD, color="white"),
                        ],
                        spacing=3,
                    ),
                ],
                spacing=3,
            ),
        )