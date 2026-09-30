FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv

WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:0.11.23 /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY . .

ENV PATH="/opt/venv/bin:${PATH}"
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
