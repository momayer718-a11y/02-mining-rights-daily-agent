# RUN

## Local 5 Minute Check

```bash
cd /Users/Zhuanz/Desktop/面试题目MVP/02-mining-rights-daily-agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
make brief
cat outputs/generated/pilbara_daily.md
```

Start the Web console:

```bash
make console
open http://localhost:8002
```

## Docker

```bash
cd /Users/Zhuanz/Desktop/面试题目MVP/02-mining-rights-daily-agent
docker compose up --build
```

Open `http://localhost:8002` after startup.

## Optional Live Model

```bash
cp .env.example .env
export MODEL_API_KEY=your_key
export MODEL_BASE_URL=https://api.deepseek.com
export MODEL_NAME=deepseek-v4-pro
export MODEL_THINKING_ENABLED=0
export MODEL_REASONING_EFFORT=medium
export MODEL_MAX_TOKENS=1800
export MODEL_KEY_PASSPHRASE=your_local_decryption_passphrase
```

The app reads `MODEL_API_KEY` first. If it is empty, it can decrypt `config/model_api_key.enc.json` with `MODEL_KEY_PASSPHRASE`; commit only the encrypted JSON, not a plaintext `.env`.

The example keeps `MODEL_THINKING_ENABLED=0` for stable demo latency. Set it to `1` only when you explicitly want DeepSeek V4 Pro thinking output.

## Brief Smoke Test

```bash
curl -s http://localhost:8002/brief \
  -H 'content-type: application/json' \
  -d '{"prompt":"给我生成一份关于 Indonesia nickel 的今日简报"}' | jq
```

Expected shape: Chinese Markdown brief, complete workflow trace, `limited` warnings when evidence is missing, and Raw Tool Output folded in the Web console.

## QA And Package

```bash
make test
make qa
make package
```

`make qa` writes fresh reports under `outputs/generated/` so clone-time verification does not modify tracked files. Set `QA_UPDATE_TRACKED_REPORTS=1` only when intentionally refreshing `QA_REPORT.md` and `qa/reports/*.json`. `make package` writes `/Users/Zhuanz/Desktop/02-mining-rights-daily-agent-tool.zip`.

## MCP Server Commands

```bash
python3 -m servers.mining_news_mcp
python3 -m servers.mineral_pdf_mcp
python3 -m servers.lme_price_mcp
```

## Claude Desktop / Cursor

Use `mcp-config.json` as the starting config and adjust paths if the project is moved.
