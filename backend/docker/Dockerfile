ARG PYTHON_IMAGE=python:3.11-slim-bookworm@sha256:528257d48c1da0dcecc2e725d1ae34498d60c965f1241e39cd6a85a8859bdf84
FROM ${PYTHON_IMAGE} AS builder
COPY --from=ghcr.io/astral-sh/uv:0.8.13@sha256:4de5495181a281bc744845b9579acf7b221d6791f99bcc211b9ec13f417c2853 /uv /usr/local/bin/uv
ENV UV_PROJECT_ENVIRONMENT=/opt/venv UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never
WORKDIR /build
COPY pyproject.toml uv.lock README.md ./
COPY drf_admin ./drf_admin
RUN uv sync --frozen --no-dev --no-editable

FROM ${PYTHON_IMAGE}
ENV PATH="/opt/venv/bin:$PATH" VIRTUAL_ENV=/opt/venv ENVIRONMENT=pro \
    PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 TZ=Asia/Shanghai
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /usr/local/bin/uv /usr/local/bin/uv
COPY manage.py ./manage.py
COPY docker/production.env /opt/venv/lib/python3.11/site-packages/.env.pro
RUN groupadd -g 10001 appgroup && useradd -u 10001 -g appgroup appuser \
    && mkdir -p /opt/venv/lib/python3.11/site-packages/logs /data/db \
    && chown 10001:10001 /opt/venv/lib/python3.11/site-packages/logs /data/db
USER 10001:10001
EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=6s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/ready', timeout=5)" || exit 1
CMD ["gunicorn", "drf_admin.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--access-logfile", "-", "--error-logfile", "-"]
