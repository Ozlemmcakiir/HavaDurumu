FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLET_HOST=0.0.0.0 \
    FLET_PORT=8080

# 1. Çalışma dizinini oluştur ve ayarla
WORKDIR /app

# 2. Kullanıcıyı oluştur ve /app dizininin sahipliğini ver
RUN useradd --create-home --uid 1000 appuser \
    && chown -R appuser:appuser /app

# 3. Bağımlılıkları ve dosyaları kopyala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py weather_app.py weather_service.py weather_utils.py location_service.py ./
COPY assets/ ./assets/

# 4. Kopyalanan yeni dosyaların sahipliğini appuser'a ver
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8080

CMD ["python", "main.py"]