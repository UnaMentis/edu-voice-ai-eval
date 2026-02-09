# ──────────────────────────────────────────────────────────
# edu-voice-ai-eval – multi-stage Docker build
# ──────────────────────────────────────────────────────────

# --- Stage 1: Build the Next.js web dashboard ---
FROM node:22-alpine AS web-builder
WORKDIR /app/web
COPY web/package.json web/package-lock.json ./
RUN npm ci --production=false
COPY web/ ./
RUN npx next build

# --- Stage 2: Python API + pre-built dashboard ---
FROM python:3.11-slim AS runtime

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    nodejs npm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e "." && pip install --no-cache-dir uvicorn

# Copy the Python package
COPY voicelearn_eval/ voicelearn_eval/
COPY configs/ configs/

# Copy pre-built web dashboard
COPY --from=web-builder /app/web/.next web/.next
COPY --from=web-builder /app/web/public web/public
COPY --from=web-builder /app/web/package.json web/package.json
COPY --from=web-builder /app/web/node_modules web/node_modules
COPY --from=web-builder /app/web/next.config.ts web/next.config.ts

# Data directory (SQLite DB, exports, etc.)
RUN mkdir -p /data
ENV VOICELEARN_EVAL_DB_PATH=/data/eval.db

# Expose ports: API (3201) + Web (3200)
EXPOSE 3200 3201

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:3201/api/eval/health')" || exit 1

# Start both services
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
ENTRYPOINT ["docker-entrypoint.sh"]
