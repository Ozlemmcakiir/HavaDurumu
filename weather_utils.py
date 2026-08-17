import flet as ft


class WeatherTheme:
    """Tek yerden yönetilen görsel sabitler (orijinal q1/q2 paleti)."""

    AMBER = "#F2A65A"
    CYAN = "#6FD3E0"
    TEXT = "#F5F3EE"
    MUTED = "#98A2B3"
    CARD_BG = "#1A2333"
    CARD_BORDER = "#88A8ED"
    BG_DARK = "#0B1220"
    METRIC_BG = "#1F2A3D"
    METRIC_BORDER = "#2A3547"
    BAR_TRACK = "#2A3547"
    ROW_DIVIDER = "#212B3D"


class WeatherUtils:
    """Hava kodlarını açıklama, ikon ve gökyüzü gradyanına çevirir."""

    WEATHER_DESC = {
        0: "Açık",
        1: "Genelde açık",
        2: "Parçalı bulutlu",
        3: "Kapalı",
        45: "Sisli",
        48: "Kırağı sisi",
        51: "Hafif çisenti",
        53: "Çisenti",
        55: "Yoğun çisenti",
        56: "Donan çisenti",
        57: "Yoğun donan çisenti",
        61: "Hafif yağmur",
        63: "Yağmur",
        65: "Kuvvetli yağmur",
        66: "Donan hafif yağmur",
        67: "Donan kuvvetli yağmur",
        71: "Hafif kar",
        73: "Kar",
        75: "Kuvvetli kar",
        77: "Kar taneleri",
        80: "Hafif sağanak",
        81: "Sağanak",
        82: "Kuvvetli sağanak",
        85: "Hafif kar sağanağı",
        86: "Kuvvetli kar sağanağı",
        95: "Gök gürültülü fırtına",
        96: "Dolulu fırtına",
        99: "Kuvvetli dolulu fırtına",
    }

    @classmethod
    def get_description(cls, code):
        return cls.WEATHER_DESC.get(code, "Bilinmiyor")

    @staticmethod
    def get_icon(code, is_day=True):
        """WMO kodu -> (ikon, renk). Orijinal q1/q2 eşlemesi."""
        theme = WeatherTheme

        if code in (0, 1):
            return (
                ft.Icons.WB_SUNNY_ROUNDED if is_day else ft.Icons.NIGHTLIGHT_ROUND,
                theme.AMBER if is_day else "#DCE3EC",
            )
        if code == 2:
            return (
                ft.Icons.WB_CLOUDY_ROUNDED,
                theme.AMBER if is_day else "#B9C3CE",
            )
        if code == 3:
            return (ft.Icons.CLOUD_ROUNDED, "#C9D3DD")
        if code in (45, 48):
            return (ft.Icons.FOGGY, "#AEB9C4")
        if code in (51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82):
            return (ft.Icons.WATER_DROP_ROUNDED, theme.CYAN)
        if code in (71, 73, 75, 77, 85, 86):
            return (ft.Icons.AC_UNIT_ROUNDED, "#EAF3F6")
        if code in (95, 96, 99):
            return (ft.Icons.THUNDERSTORM_ROUNDED, theme.AMBER)
        return (ft.Icons.CLOUD_ROUNDED, theme.MUTED)

    @staticmethod
    def get_gradient(is_day, code):
        if code in (95, 96, 99):
            return ["#0d1117", "#1b2333"]
        if code in (71, 73, 75, 77, 85, 86):
            return ["#1c2534", "#3a4a5e"]
        if is_day:
            return ["#1c4d8f", "#4f9fc9"]
        return ["#050914", "#131c33"]
