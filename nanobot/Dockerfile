ARG REGISTRY_PREFIX_DOCKER_HUB
FROM ${REGISTRY_PREFIX_DOCKER_HUB}python:3.14.2-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 LANG=C.UTF-8

# Install nanobot-ai first
RUN pip install --no-cache-dir "nanobot-ai @ https://github.com/HKUDS/nanobot/archive/e7d371ec1e6531b28898ec2c869ef338e8dd46ec.zip"

# Setup user
ARG APP_UID=1001
ARG APP_GID=1001
RUN groupadd --system --gid ${APP_GID} appgroup && useradd --system --gid ${APP_GID} --uid ${APP_UID} --create-home appuser

# Copy application files
COPY --chown=appuser:appgroup entrypoint.py config.json /app/nanobot/
COPY --chown=appuser:appgroup workspace/ /app/nanobot/workspace/

# Give write permissions to workspace
RUN chmod -R 777 /app/nanobot/workspace

USER appuser
WORKDIR /app/nanobot
CMD ["python", "/app/nanobot/entrypoint.py"]
