# kurcalama

import flet as ft                                                                                                                 # OK      
import requests                                                                                                                   # OK 
from datetime import datetime                                                                                                     # OK 

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"                                                                    # OK 
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"                                                                           # OK 

AMBER = "#F3C18F"                                                                                                               # OK 
CYAN = "#7BD3DF"                                                                                                          # OK 
TEXT = "#6FA7DD"                                                                                                              # OK 
MUTED = "#D4BFCF"                                                                                                            # OK 
CARD_BG = "#5A63A3"                                                                                                              # OK 
CARD_BORDER = "#E175A2C2"                                                                                                        # OK 
BG_DARK = "#72ADCA"                                                                                                           # OK 

WEATHER_DESC = {                                                                                                                  # OK 
    0: "Açık", 1: "Genelde açık", 2: "Parçalı bulutlu", 3: "Kapalı",                                                              # OK 
    45: "Sisli", 48: "Kırağı sisi",                                                                                               # OK 
    51: "Hafif çisenti", 53: "Çisenti", 55: "Yoğun çisenti",                                                                      # OK 
    56: "Donan çisenti", 57: "Yoğun donan çisenti",                                                                               # OK 
    61: "Hafif yağmur", 63: "Yağmur", 65: "Kuvvetli yağmur",                                                                      # OK 
    66: "Donan hafif yağmur", 67: "Donan kuvvetli yağmur",                                                                        # OK 
    71: "Hafif kar", 73: "Kar", 75: "Kuvvetli kar", 77: "Kar taneleri",                                                           # OK 
    80: "Hafif sağanak", 81: "Sağanak", 82: "Kuvvetli sağanak",                                                                   # OK 
    85: "Hafif kar sağanağı", 86: "Kuvvetli kar sağanağı",                                                                        # OK 
    95: "Gök gürültülü fırtına", 96: "Dolulu fırtına", 99: "Kuvvetli dolulu fırtına",                                             # OK 
}                                                                                                                                 # OK 


def icon_for(code: int, is_day: bool = True):                                                                                     # OK 
    """Weather code -> (ikon, renk) eşlemesi."""
    if code in (0, 1):
        return (ft.Icons.WB_SUNNY_ROUNDED if is_day else ft.Icons.NIGHTLIGHT_ROUND, AMBER if is_day else "#DCE3EC")
    if code == 2:
        return (ft.Icons.WB_CLOUDY_ROUNDED, AMBER if is_day else "#B9C3CE")
    if code == 3:
        return (ft.Icons.CLOUD_ROUNDED, "#C9D3DD")
    if code in (45, 48):
        return (ft.Icons.FOGGY, "#AEB9C4")
    if code in (51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82):
        return (ft.Icons.WATER_DROP_ROUNDED, CYAN)
    if code in (71, 73, 75, 77, 85, 86):
        return (ft.Icons.AC_UNIT_ROUNDED, "#EAF3F6")
    if code in (95, 96, 99):
        return (ft.Icons.THUNDERSTORM_ROUNDED, AMBER)
    return (ft.Icons.CLOUD_ROUNDED, MUTED)


def sky_gradient(is_day: bool, code: int):
    if code in (95, 96, 99):
        return ["#0d1117", "#1b2333"]
    if code in (71, 73, 75, 77, 85, 86):
        return ["#1c2534", "#3a4a5e"]
    if is_day:
        return ["#1c4d8f", "#4f9fc9"]
    return ["#050914", "#131c33"]


def main(page: ft.Page):
    page.title = "Gökyüzü — Hava Durumu"
    page.window.width = 460
    page.window.height = 780
    page.window.min_width = 380
    page.padding = 0
    page.bgcolor = BG_DARK
    page.fonts = {
        "Display": "https://raw.githubusercontent.com/google/fonts/main/ofl/spacegrotesk/SpaceGrotesk[wght].ttf",
    }
    page.theme = ft.Theme(font_family="Inter")

    state = {"results": []}

    # ---------- Üst arama alanı ----------
    search_field = ft.TextField(
        hint_text="Şehir veya ülke ara — örn. İzmir, Tokyo, Cape Town",
        border_radius=14,
        border_color=CARD_BORDER,
        focused_border_color=AMBER,
        bgcolor=CARD_BG,
        color=TEXT,
        hint_style=ft.TextStyle(color=MUTED),
        prefix_icon=ft.Icons.SEARCH_ROUNDED,
        height=52,
        content_padding=ft.Padding.symmetric(horizontal=14, vertical=8),
    )

    suggestions_list = ft.Column(spacing=0, visible=False)
    suggestions_card = ft.Container(
        content=suggestions_list,
        bgcolor=CARD_BG,
        border=ft.Border.all(1, CARD_BORDER),
        border_radius=14,
        padding=4,
        visible=False,
    )

    # ---------- Ana panel (bugünkü hava) ----------
    city_name_txt = ft.Text("", size=20, weight=ft.FontWeight.W_600, color=TEXT, font_family="Display")
    city_meta_txt = ft.Text("", size=13, color=MUTED)
    coords_txt = ft.Text("", size=11, color=MUTED, font_family="monospace")
    temp_txt = ft.Text("--°", size=64, weight=ft.FontWeight.BOLD, color=TEXT, font_family="Display")
    desc_txt = ft.Text("—", size=15, color=MUTED)
    main_icon = ft.Icon(ft.Icons.CLOUD_ROUNDED, size=84, color=MUTED)

    wind_txt = ft.Text("--", size=15, color=TEXT, font_family="monospace")
    humidity_txt = ft.Text("--", size=15, color=TEXT, font_family="monospace")
    sun_txt = ft.Text("-- / --", size=12, color=TEXT, font_family="monospace")

    def metric_box(label, value_control, icon):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(label.upper(), size=10, color=MUTED, weight=ft.FontWeight.W_500),
                    ft.Row([ft.Icon(icon, size=14, color=AMBER), value_control], spacing=6),
                ],
                spacing=4,
            ),
            bgcolor="#1F2A3D",
            border=ft.Border.all(1, "#2A3547"),
            border_radius=12,
            padding=10,
            expand=True,
        )

    metrics_row = ft.Row(
        [
            metric_box("Rüzgar", wind_txt, ft.Icons.AIR_ROUNDED),
            metric_box("Nem", humidity_txt, ft.Icons.WATER_DROP_OUTLINED),
            metric_box("Gündoğ./Batım", sun_txt, ft.Icons.WB_TWILIGHT),
        ],
        spacing=10,
    )

    main_panel = ft.Container(
        content=ft.Column(
            [
                ft.Row([city_name_txt, city_meta_txt], spacing=8),
                coords_txt,
                ft.Row(
                    [
                        ft.Column([temp_txt, desc_txt], spacing=2),
                        main_icon,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                metrics_row,
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

    loader = ft.Container(
        content=ft.ProgressRing(color=AMBER, width=32, height=32),
        alignment=ft.Alignment.CENTER,
        padding=30,
        visible=False,
    )

    # ---------- Saatlik şerit ----------
    hourly_row = ft.Row(spacing=10, scroll=ft.ScrollMode.AUTO)
    hourly_section = ft.Column(
        [
            ft.Text("SONRAKİ 24 SAAT", size=12, color=MUTED, weight=ft.FontWeight.W_600),
            hourly_row,
        ],
        spacing=8,
        visible=False,
    )

    # ---------- Günlük liste ----------
    daily_col = ft.Column(spacing=0)
    daily_section = ft.Column(
        [
            ft.Text("7 GÜNLÜK TAHMİN", size=12, color=MUTED, weight=ft.FontWeight.W_600),
            ft.Container(
                content=daily_col,
                bgcolor=CARD_BG,
                border=ft.Border.all(1, CARD_BORDER),
                border_radius=16,
                padding=6,
            ),
        ],
        spacing=8,
        visible=False,
    )

    # ---------- API çağrıları ----------
    def run_search(e):
        query = search_field.value.strip()
        if len(query) < 2:
            suggestions_card.visible = False
            page.update()
            return
        try:
            resp = requests.get(
                GEOCODE_URL,
                params={"name": query, "count": 8, "language": "tr", "format": "json"},
                timeout=10,
            )
            resp.raise_for_status()
            results = resp.json().get("results", []) or []
        except Exception:
            results = []
        state["results"] = results
        render_suggestions(results)

    def render_suggestions(results):
        suggestions_list.controls.clear()
        if not results:
            suggestions_list.controls.append(
                ft.Container(ft.Text("Sonuç bulunamadı.", color=MUTED, size=13), padding=12)
            )
        else:
            for r in results:
                meta = ", ".join(p for p in [r.get("admin1"), r.get("country")] if p)
                suggestions_list.controls.append(
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Text(r["name"], color=TEXT, size=14),
                                ft.Text(meta, color=MUTED, size=12),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        padding=ft.Padding.symmetric(horizontal=12, vertical=10),
                        border_radius=10,
                        ink=True,
                        on_click=lambda e, place=r: select_place(place),
                    )
                )
        suggestions_card.visible = True
        suggestions_list.visible = True
        page.update()

    def select_place(place):
        search_field.value = f"{place['name']}, {place.get('country', '')}"
        suggestions_card.visible = False
        page.update()
        load_weather(place)

    def load_weather(place):
        loader.visible = True
        main_panel.visible = False
        hourly_section.visible = False
        daily_section.visible = False
        page.update()

        try:
            resp = requests.get(
                FORECAST_URL,
                params={
                    "latitude": place["latitude"],
                    "longitude": place["longitude"],
                    "current_weather": "true",
                    "hourly": "temperature_2m,relative_humidity_2m,weathercode",
                    "daily": "weathercode,temperature_2m_max,temperature_2m_min,sunrise,sunset",
                    "timezone": "auto",
                },
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as ex:
            loader.visible = False
            page.show_dialog(ft.SnackBar(ft.Text(f"Hava durumu alınamadı: {ex}")))
            page.update()
            return

        render_weather(place, data)
        loader.visible = False
        main_panel.visible = True
        hourly_section.visible = True
        daily_section.visible = True
        page.update()

    def render_weather(place, data):
        cw = data["current_weather"]
        is_day = cw.get("is_day", 1) == 1
        icon, icon_color = icon_for(cw["weathercode"], is_day)

        city_name_txt.value = place["name"]
        city_meta_txt.value = ", ".join(p for p in [place.get("admin1"), place.get("country")] if p)
        coords_txt.value = f"{place['latitude']:.2f}°, {place['longitude']:.2f}°  ·  {data.get('timezone', '')}"
        temp_txt.value = f"{round(cw['temperature'])}°"
        desc_txt.value = WEATHER_DESC.get(cw["weathercode"], "Bilinmiyor")
        main_icon.name = icon
        main_icon.color = icon_color

        main_panel.gradient = ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT,
            end=ft.Alignment.BOTTOM_RIGHT,
            colors=sky_gradient(is_day, cw["weathercode"]),
        )

        wind_txt.value = f"{round(cw['windspeed'])} km/s"

        # en yakın saatteki nem
        now = datetime.now()
        hourly_times = [datetime.fromisoformat(t) for t in data["hourly"]["time"]]
        closest_idx = min(range(len(hourly_times)), key=lambda i: abs(hourly_times[i] - now))
        humidity_txt.value = f"{data['hourly']['relative_humidity_2m'][closest_idx]}%"

        sunrise = datetime.fromisoformat(data["daily"]["sunrise"][0]).strftime("%H:%M")
        sunset = datetime.fromisoformat(data["daily"]["sunset"][0]).strftime("%H:%M")
        sun_txt.value = f"{sunrise} / {sunset}"

        # saatlik şerit
        hourly_row.controls.clear()
        start_idx = next((i for i, t in enumerate(hourly_times) if t >= now), 0)
        for i in range(start_idx, min(start_idx + 24, len(hourly_times))):
            h_icon, h_color = icon_for(data["hourly"]["weathercode"][i], 6 <= hourly_times[i].hour < 20)
            hourly_row.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("Şimdi" if i == start_idx else hourly_times[i].strftime("%H:%M"),
                                    size=11, color=MUTED, font_family="monospace"),
                            ft.Icon(h_icon, size=22, color=h_color),
                            ft.Text(f"{round(data['hourly']['temperature_2m'][i])}°",
                                    size=14, weight=ft.FontWeight.W_600, color=TEXT),
                        ],
                        spacing=6,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    bgcolor=CARD_BG,
                    border=ft.Border.all(1, CARD_BORDER),
                    border_radius=14,
                    padding=ft.Padding.symmetric(vertical=12, horizontal=6),
                    width=64,
                )
            )

        # günlük liste
        daily_col.controls.clear()
        day_names = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
        daily = data["daily"]
        all_temps = daily["temperature_2m_max"] + daily["temperature_2m_min"]
        tmax, tmin = max(all_temps), min(all_temps)
        span = (tmax - tmin) or 1
        for i, t in enumerate(daily["time"]):
            d = datetime.fromisoformat(t)
            label = "Bugün" if i == 0 else day_names[d.weekday()]
            d_icon, d_color = icon_for(daily["weathercode"][i], True)
            lo, hi = daily["temperature_2m_min"][i], daily["temperature_2m_max"][i]
            left_pct = (lo - tmin) / span
            width_pct = (hi - lo) / span
            daily_col.controls.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Container(ft.Text(label, size=13, color=TEXT), width=70),
                            ft.Icon(d_icon, size=20, color=d_color),
                            ft.Container(ft.Text(f"{round(lo)}°", size=12, color=MUTED, font_family="monospace"), width=32,
                                         alignment=ft.Alignment.CENTER),
                            ft.Container(
                                content=ft.Stack(
                                    [
                                        ft.Container(bgcolor="#2A3547", border_radius=3, height=4, expand=True),
                                        ft.Container(
                                            bgcolor=AMBER,
                                            border_radius=3,
                                            height=4,
                                            margin=ft.Margin.only(left=left_pct * 140, right=0),
                                            width=max(width_pct * 140, 6),
                                        ),
                                    ]
                                ),
                                width=140,
                            ),
                            ft.Container(ft.Text(f"{round(hi)}°", size=12, color=TEXT, font_family="monospace"), width=32,
                                         alignment=ft.Alignment.CENTER),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=ft.Padding.symmetric(vertical=10, horizontal=8),
                    border=ft.Border.only(bottom=ft.BorderSide(1, "#212B3D")) if i < len(daily["time"]) - 1 else None,
                )
            )

    search_field.on_change = run_search
    search_field.on_submit = run_search

    page.add(
        ft.Container(
            content=ft.Column(
                [
                    search_field,
                    suggestions_card,
                    loader,
                    main_panel,
                    hourly_section,
                    daily_section,
                    ft.Text("Veri kaynağı: Open-Meteo", size=11, color=MUTED, text_align=ft.TextAlign.CENTER),
                ],
                spacing=18,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=20,
            expand=True,
        )
    )

    # Varsayılan: Ankara ile başla
    load_weather({"name": "Ankara", "admin1": "Ankara", "country": "Türkiye", "latitude": 39.92, "longitude": 32.85})


#if __name__ == "__main__":                            bu kısımda uygulama şeklinde çalışan kod 
#    ft.run(main)

if __name__ == "__main__":
    ft.run(main, view=ft.AppView.WEB_BROWSER)      #   bu kısımda web sayfası şeklinde çalışan kod