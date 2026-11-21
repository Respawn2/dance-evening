FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# Переменные uv: ставить в системное окружение, не копировать файлы из кеша
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Зависимости — отдельным слоем, до копирования кода.
# Слой переиспользуется, пока pyproject.toml и uv.lock не изменились.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Код — последним, он меняется чаще всего
COPY README.md ./
COPY src/ ./src/
RUN uv sync --frozen --no-dev

# Процесс не должен работать от root
RUN useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app
USER appuser

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8080

# Версия подставляется при сборке: --build-arg APP_VERSION=$(git describe --tags)
ARG APP_VERSION=0.0.0-dev
ENV APP_VERSION=$APP_VERSION

CMD ["python", "-m", "evenings"]
