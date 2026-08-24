FROM python:3.14.7-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLET_FORCE_WEB_SERVER=true \
    FLET_SERVER_IP=0.0.0.0 \
    FLET_SERVER_PORT=8000

WORKDIR /app

RUN useradd --create-home --uid 1000 appuser \
    && chown -R appuser:appuser /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py weather_app.py weather_service.py weather_utils.py location_service.py ./
COPY assets/ ./assets/

RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["python", "main.py"]
