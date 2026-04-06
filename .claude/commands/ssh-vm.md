Run a command on the deploy VM (10.93.24.120) via the relay API.

Arguments: $ARGUMENTS (the shell command to run on the VM, e.g. `docker ps` or `cat ~/.qwen/oauth_creds.json`)

## How it works

The deploy VM is at `10.93.24.120` on the university internal network. It is NOT directly reachable via SSH. The ONLY way to run commands is through the relay API on the autochecker dashboard.

**NEVER try `ssh deploy@10.93.24.120` or `ssh -J ... deploy@10.93.24.120` — both will fail.**

## Steps

1. Get the RELAY_TOKEN from Hetzner:

```bash
RELAY_TOKEN=$(ssh nurios@188.245.43.68 "grep RELAY_TOKEN ~/autochecker/deploy/.env | cut -d= -f2" 2>/dev/null)
```

2. Run the command via the relay API:

```bash
curl -s -X POST \
  -H "Authorization: Bearer $RELAY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"host":"10.93.24.120","port":22,"username":"deploy","command":"THE_COMMAND","timeout":30}' \
  https://auche.namaz.live/relay/ssh
```

3. The response is JSON: `{"exit_code": 0, "stdout": "...", "stderr": "...", "error": "..."}`
   - Parse and show stdout to the user
   - If exit_code != 0, show stderr too
   - If error is non-empty, the relay itself failed (e.g. SSH timeout)

## Error handling

- **HTTP 503** — relay worker is disconnected. Check status: `ssh nurios@188.245.43.68 "docker exec autochecker-bot curl -s http://dashboard:8000/relay/status"`
- **HTTP 403** — wrong RELAY_TOKEN
- **`"error": "timeout"`** — command took too long, increase timeout (max 120)

## What runs on this VM

- `~/qwen-code-oai-proxy/` — Qwen Code API proxy (Docker, port 42005)
- `~/se-toolkit-lab-7/` — Lab 7 services (Docker, ports 42001-42004)
- `~/.qwen/oauth_creds.json` — Qwen OAuth tokens
- Relay worker (systemd service `relay-worker`)
