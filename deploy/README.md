# Deployment

Deploy the autochecker Telegram bot and web dashboard using Docker.

## Quick Start (new server)

```bash
# 1. Clone with submodules
git clone --recurse-submodules git@github.com:inno-se-toolkit/labs-software-engineering-toolkit.git ~/auche
cd ~/auche

# 2. Create .env from template
cp deploy/.env.example deploy/.env
nano deploy/.env   # fill in BOT_TOKEN, GITHUB_TOKEN, OPENROUTER_API_KEY

# 3. Build and start
docker compose -f deploy/docker-compose.yml up -d

# 4. Set up nginx (adjust port if needed)
#    Proxy auche.namaz.live -> 127.0.0.1:8082
#    Then: sudo certbot --nginx -d auche.namaz.live
```

## Update

```bash
cd ~/auche && ./deploy/update.sh
```

## Services

| Service | Container | Port | Description |
|---------|-----------|------|-------------|
| bot | autochecker-bot | none | Telegram bot (polling) |
| dashboard | autochecker-dashboard | 127.0.0.1:8082 | Web scoreboard |

## Logs

```bash
docker compose -f deploy/docker-compose.yml logs bot -f --tail 50
docker compose -f deploy/docker-compose.yml logs dashboard --tail 50
```
