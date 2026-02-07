#!/bin/bash
set -e
cd "$(dirname "$0")/.."

echo "==> Pulling main repo..."
git pull origin main

echo "==> Updating submodules..."
git submodule update --remote autochecker tg_bot_autochecker

echo "==> Building..."
docker compose -f deploy/docker-compose.yml build

echo "==> Restarting..."
docker compose -f deploy/docker-compose.yml up -d

echo "==> Status:"
docker compose -f deploy/docker-compose.yml ps
echo ""
echo "==> Recent logs:"
docker compose -f deploy/docker-compose.yml logs --tail 5
