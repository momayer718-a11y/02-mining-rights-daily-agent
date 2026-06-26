# Mining Rights Daily Agent Console

## 项目简介

Mining Rights Daily Agent Console 是一个面向矿业主题的日报生成智能体。用户输入主题，例如 `给我生成一份关于 Pilbara 锂矿的今日简报`，系统会完成意图识别、工具调用、工作流追踪和中文 Markdown 简报生成。

Mining Rights Daily Agent Console is a daily brief agent for mining-industry topics. A user enters a prompt such as `给我生成一份关于 Pilbara 锂矿的今日简报`, and the system handles intent parsing, tool orchestration, workflow tracing and structured Chinese Markdown brief generation.

## 核心能力 / Key Features

- 工作流画布 / Workflow canvas: User Input -> Planner -> mining news, resource PDF and price tools -> Brief Synthesizer -> Markdown Output.
- 多主题解析 / Multi-topic parsing: 支持锂、镍、铜、稀土、铁矿石、锌等矿业主题的中文、英文和中英混合输入。
- 结构化简报 / Structured brief: 输出执行摘要、新闻摘要、资源量/储量、价格走势、风险提示、引用来源和数据缺口。
- DeepSeek V4 Pro 支持 / DeepSeek V4 Pro support: 支持加密 key fallback，也支持无 live model 的本地模板运行。
- 可测试交付 / Testable delivery: 包含单元测试、QA 报告、Docker 运行方式和独立打包命令。

## 最新验证 / Latest Validation

| Check | Result |
| --- | --- |
| Unit tests | 6 passed |
| Local fallback | Runnable without a live model key |

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

`make qa` runs multi-topic brief cases including Pilbara lithium, Peru copper, Indonesia nickel, China rare earth, DRC cobalt, iron ore, zinc, gold, uranium and graphite. Fresh QA artifacts are written under `outputs/generated/` by default; set `QA_UPDATE_TRACKED_REPORTS=1` only when intentionally refreshing the checked-in report snapshots. `make package` creates `/Users/Zhuanz/Desktop/02-mining-rights-daily-agent-tool.zip`.

## MCP Client Config

`mcp-config.json` is included for Claude Desktop / Cursor-style MCP clients. Adjust absolute paths if the project is moved.

## Boundaries

This is a local mining brief-generation tool, not a production data room or financial-advice product. For production use, connect the workflow to governed enterprise data and review outputs through the normal compliance process.
