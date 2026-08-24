#!/bin/sh
set -e

# Bağımlılıkları yükle
pip install --no-cache-dir -q -r requirements-dev.txt || pip install --no-cache-dir -q pytest

# Rapor klasörünü oluştur
mkdir -p reports

# Kod derleme kontrolleri
python -m py_compile weather_app.py weather_service.py weather_utils.py location_service.py

# PYTHONPATH'e proje kök dizinini ekleyerek pytest'i çalıştır
PYTHONPATH=. pytest -q --junitxml=reports/junit.xml

echo "CI test aşaması tamam."