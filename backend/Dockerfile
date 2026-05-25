FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/apps

RUN apt-get update && apt-get install -y --no-install-recommends \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    libsqlite3-mod-spatialite \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# GeoDjango — resolve actual .so paths on Debian bookworm
RUN GDAL_SO=$(find /usr/lib -name 'libgdal.so*' -type f 2>/dev/null | head -1) && \
    GEOS_SO=$(find /usr/lib -name 'libgeos_c.so*' -type f 2>/dev/null | head -1) && \
    echo "GDAL_LIBRARY_PATH=$GDAL_SO" >> /etc/environment && \
    echo "GEOS_LIBRARY_PATH=$GEOS_SO" >> /etc/environment
ENV GDAL_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgdal.so
ENV GEOS_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgeos_c.so

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data/nasa_cache /app/media /app/staticfiles

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
