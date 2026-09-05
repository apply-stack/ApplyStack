FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY pyproject.toml ./
COPY app ./app
RUN pip install --upgrade pip \
    && pip install -e . \
    && pip install --group dev

COPY . .

# Never run as root, even in development.
RUN useradd --create-home --uid 1000 appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# docker-compose.yml overrides this with --reload for development.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
