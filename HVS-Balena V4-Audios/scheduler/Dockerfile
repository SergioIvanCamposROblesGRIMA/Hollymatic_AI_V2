# Imagen ligera para el agendador de luces Wiz + apagado del KP200.
FROM balenalib/raspberrypi4-64-debian-python:3.11-bookworm-run

ENV PYTHONUNBUFFERED=1
ENV TZ=America/Los_Angeles

# tzdata para que el cron de APScheduler dispare en hora local correcta (igual que el Dockerfile principal).
RUN apt-get update && apt-get install -y --no-install-recommends tzdata \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
    && dpkg-reconfigure -f noninteractive tzdata \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN mkdir -p /secrets

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir --break-system-packages -r requirements.txt

COPY src/ ./src/
COPY main.py .
COPY start.sh .
COPY tests/ ./tests/

RUN chmod +x ./start.sh

# start.sh hidrata la cuenta de servicio (GCP_SA_B64/GCP_SA_JSON) y luego ejecuta main.py.
CMD ["./start.sh"]
