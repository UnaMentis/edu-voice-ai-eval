#!/bin/bash
set -e

echo "Starting VoiceLearn Eval..."

# Start Next.js in production mode (background)
cd /app/web
PORT=3200 npx next start --port 3200 &
WEB_PID=$!

# Start FastAPI
cd /app
exec uvicorn voicelearn_eval.api.app:create_app \
    --host 0.0.0.0 \
    --port 3201 \
    --factory \
    --workers "${WORKERS:-1}"
