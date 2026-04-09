# syntax=docker/dockerfile:1

# --- Frontend: Vue + Vite + Tailwind → static/dist
FROM node:20-alpine AS frontend
WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# --- Backend: FastAPI (no Tkinter — do not import main.py)
FROM python:3.12-slim-bookworm

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    ANDROIDTV_PORT=8765

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    "fastapi>=0.115" \
    "uvicorn[standard]>=0.32" \
    "androidtvremote2>=0.3.1" \
    "zeroconf>=0.148.0"

COPY web.py tv_core.py ./

COPY --from=frontend /app/static/dist ./static/dist

# Default compose uses network_mode: host (Linux) so this process shares the PC’s
# network — mDNS discovery matches running on the host. With bridge + -p, use Connect by IP.
EXPOSE 8765

# main.py pulls in Tkinter; container only serves web:app
CMD ["sh", "-c", "exec python -m uvicorn web:app --host 0.0.0.0 --port ${ANDROIDTV_PORT:-8765}"]
