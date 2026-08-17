# Gökyüzü — Hava Durumu

Open-Meteo verisiyle çalışan Flet web uygulaması.

## Çalıştırma (Python 3.12)

```powershell
py -3.12 -m pip install -r requirements.txt
py -3.12 main.py
```

Uygulama tarayıcıda açılır. Varsayılan şehir Ankara'dır.

## Docker

```powershell
docker build -t havadurumu:0.1.0 .
docker run --rm -p 8080:8080 havadurumu:0.1.0
```

Tarayıcıda `http://localhost:8080` adresini aç.

## Yapı

- `main.py` — giriş noktası
- `weather_app.py` — arayüz orkestrasyonu
- `location_service.py` — şehir arama (geocoding)
- `weather_service.py` — hava durumu API
- `weather_utils.py` — ikon, açıklama ve tema
