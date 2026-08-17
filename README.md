# Gökyüzü — Hava Durumu

Open-Meteo verisiyle çalışan Flet web uygulaması.

## Çalıştırma (Python 3.12)

```powershell
py -3.12 -m pip install -r requirements.txt
py -3.12 main.py
```

Uygulama tarayıcıda açılır. Varsayılan şehir Ankara'dır.

## Yapı

- `main.py` — giriş noktası
- `weather_app.py` — arayüz orkestrasyonu
- `location_service.py` — şehir arama (geocoding)
- `weather_service.py` — hava durumu API
- `weather_utils.py` — ikon, açıklama ve tema
