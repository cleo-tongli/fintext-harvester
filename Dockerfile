FROM python:3.11-slim AS builder
ENV PIP_DISABLE_PIP_VERSION_CHECK=on PIP_NO_CACHE_DIR=off
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl ca-certificates git libxml2-dev libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /wheels
COPY requirements.txt /tmp/requirements.txt
RUN pip wheel --wheel-dir=/wheels -r /tmp/requirements.txt

FROM python:3.11-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PATH="/home/app/.local/bin:$PATH"
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl && rm -rf /var/lib/apt/lists/*
RUN useradd -ms /bin/bash app
USER app
WORKDIR /app
COPY --chown=app:app src/ /app/src/
COPY --chown=app:app scripts/ /app/scripts/
COPY --chown=app:app config/ /app/config/
COPY --chown=app:app requirements.txt /app/
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir --user /wheels/*
RUN mkdir -p /app/data/raw /app/data/bronze /app/logs
RUN curl -fsSL -o /app/supercronic https://github.com/aptible/supercronic/releases/download/v0.2.30/supercronic-linux-amd64 && chmod +x /app/supercronic
COPY --chown=app:app docker/harvest.cron /app/harvest.cron
COPY --chown=app:app docker/healthcheck.sh /app/healthcheck.sh
ENTRYPOINT ["/app/supercronic","-quiet","/app/harvest.cron"]
HEALTHCHECK --interval=1m --timeout=10s --start-period=30s --retries=3 CMD ["/app/healthcheck.sh"]
