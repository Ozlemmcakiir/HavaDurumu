FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLET_HOST=0.0.0.0 \
    FLET_PORT=8080

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py weather_app.py weather_service.py location_service.py weather_utils.py ./
COPY assets/ ./assets/

RUN useradd --create-home --uid 1000 appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

CMD ["python", "main.py"]
