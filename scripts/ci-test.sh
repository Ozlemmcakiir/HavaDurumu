#!/bin/sh
# Jenkins Test stage bu script'i python:3.12-slim konteynerinde çalıştırır.
set -e
pip install --no-cache-dir -q -r requirements-dev.txt
mkdir -p reports
python -m py_compile main.py weather_app.py weather_service.py weather_utils.py location_service.py
pytest -q --junitxml=reports/junit.xml
echo "CI test asaması tamam."
