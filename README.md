# Mining Rights Daily Agent Console

Mining Rights Daily Agent Console is a standalone mining-industry daily brief generator for interview question 2. The user enters a topic such as `给我生成一份关于 Pilbara 锂矿的今日简报`; the agent plans the request, calls three MCP-style tools, and returns a structured Chinese Markdown brief with workflow trace, source warnings and auditable raw tool output.

This repository is project 02 from the mining interview MVP set. It is fully standalone and can be evaluated, containerized or zipped independently.

Highlights:

- Agent workflow canvas: User Input -> Planner -> mining news, resource PDF and price tools -> Brief Synthesizer -> Markdown Output.
- Multi-topic intent parsing: Chinese, English and mixed prompts for lithium, nickel, copper, rare earth, iron ore, zinc and other mining topics.
- DeepSeek V4 Pro support: encrypted key fallback via `config/model_api_key.enc.json`, with template fallback when no key is available.
- Evidence boundary: unsupported commodities or missing source data return `limited` plus warnings instead of silently falling back to a default topic.
- QA-ready output: tests and QA reports cover topic variation, workflow trace integrity, unsupported-commodity handling and Markdown structure.

Latest checked result: unit tests passed locally, and the project remains runnable without a live model key through deterministic Chinese templates.

## What It Does

- Implements three independent MCP-style servers/tools:
  - `mining-news-mcp`: `search(query, days)`, `fetch_article(url)`
  - `mineral-pdf-mcp`: `extract_resources(pdf_url)`
  - `lme-price-mcp`: `get_price(commodity, date)`, `get_trend(commodity, days)`
- Parses commodity, region, topic and time window from Chinese, English or mixed prompts.
- Generates Chinese Markdown briefs with a fixed structure.
- Shows the agent workflow as a production-style canvas: User Input -> Planner -> three MCP tools -> Brief Synthesizer -> Markdown Output.
- Keeps Raw Tool Output folded by default for audit and debugging.
- Uses a live model when configured, with a Chinese template fallback when no key is present.
- Returns `limited` plus warnings for unsupported commodities or missing evidence instead of silently falling back to lithium.

## Brief Structure

```markdown
# 主题今日简报
## 一、执行摘要
## 二、新闻摘要
## 三、资源量 / 储量数据
## 四、价格走势
## 五、风险提示
## 六、引用来源
## 七、数据缺口
```

The brief body is Chinese and does not include `[ok]` or chat-style prefixes.

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
make brief
make console
```

Open `http://localhost:8002`.

Docker:

```bash
docker compose up --build
```

## Model Configuration

The app reads model settings from environment variables only. Do not commit real keys.

```bash
export MODEL_API_KEY=your_key
export MODEL_BASE_URL=https://api.deepseek.com
export MODEL_NAME=deepseek-v4-pro
export MODEL_THINKING_ENABLED=0
export MODEL_REASONING_EFFORT=medium
export MODEL_MAX_TOKENS=1800
export MODEL_KEY_PASSPHRASE=your_local_decryption_passphrase
```

When `MODEL_API_KEY` is present, the Brief Synthesizer uses the configured OpenAI-compatible chat endpoint. The example disables thinking with `MODEL_THINKING_ENABLED=0` for stable demo latency; set it to `1` only when you explicitly want DeepSeek V4 Pro thinking output. Without a key, the deterministic Chinese template keeps the demo runnable.

`config/model_api_key.enc.json` may be committed because it contains only the encrypted DeepSeek key. Runtime uses `MODEL_API_KEY` first; if it is empty, it decrypts this file with `MODEL_KEY_PASSPHRASE`.

## API Example

```bash
curl -s http://localhost:8002/brief \
  -H 'content-type: application/json' \
  -d '{"prompt":"给我生成一份关于 Indonesia nickel 的今日简报"}' | jq
```

Stable response fields include `status`, `warnings`, `source_mode`, `elapsed_ms`, `data_quality`, `intent`, `markdown` and `workflow_trace`.

## QA And Packaging

```bash
make test
make qa
make package
```

`make qa` runs multi-topic brief cases including Pilbara lithium, Peru copper, Indonesia nickel, China rare earth, DRC cobalt, iron ore, zinc, gold, uranium and graphite. `make package` creates `/Users/Zhuanz/Desktop/02-mining-rights-daily-agent-tool.zip`.

## MCP Client Config

`mcp-config.json` is included for Claude Desktop / Cursor-style MCP clients. Adjust absolute paths if the project is moved.

## Boundaries

This is a complete interview MVP, not a production data room. Fixture sources are marked as fixture data, unsupported commodities remain limited, and real paid/login sources are not bypassed.
