#!/usr/bin/env bash
set -euo pipefail

if [ ! -f .env.production ]; then
  echo "Missing .env.production. Copy .env.production.example and fill in DOMAIN and keys first."
  exit 1
fi

sudo apt-get update
sudo apt-get install -y ca-certificates curl git

if ! command -v docker >/dev/null 2>&1; then
  curl -fsSL https://get.docker.com | sudo sh
fi

sudo docker compose --env-file .env.production -f docker-compose.hostinger.yml up -d --build
sudo docker compose --env-file .env.production -f docker-compose.hostinger.yml ps
