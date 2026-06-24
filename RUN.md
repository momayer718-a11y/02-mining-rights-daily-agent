# RUN

## 本地 5 分钟验证

```bash
cd /Users/Zhuanz/Desktop/面试题目MVP/02-mining-rights-daily-agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
make brief
cat outputs/pilbara_daily.md
```

启动可视化控制台：

```bash
make console
open http://localhost:8002
```

## Docker

```bash
cd /Users/Zhuanz/Desktop/面试题目MVP/02-mining-rights-daily-agent
docker compose up --build
```

Docker 启动后访问 `http://localhost:8002`。

## 可选 APIMart / Gemini

```bash
cp .env.example .env
export APIMART_API_KEY=your_key
export APIMART_BASE_URL=https://api.apimart.ai/v1
export APIMART_MODEL=gemini-3.5-flash
```

无 key 时自动使用中文模板 fallback；不要把真实 key 写入项目文件或压缩包。

## 输出说明

- 简报正文是中文 Markdown，不带 `[ok]` 等 API 状态前缀。
- 工作流画布展示 Agent Planner、3 个 MCP server 和 Brief Synthesizer。
- Raw Tool Output 默认折叠，用于审计工具结果和 JSON。

## QA 与封装

```bash
make test
make qa
make package
```

`make qa` 生成 `QA_REPORT.md` 和 `qa/reports/*.json`。`make package` 生成 `/Users/Zhuanz/Desktop/02-mining-rights-daily-agent-tool.zip`。

## MCP server 单独启动

```bash
python3 -m servers.mining_news_mcp
python3 -m servers.mineral_pdf_mcp
python3 -m servers.lme_price_mcp
```

## Claude Desktop / Cursor

把 `mcp-config.json` 里的绝对路径改成当前机器路径后即可接入。本仓库已按 `/Users/Zhuanz/Desktop/面试题目MVP/02-mining-rights-daily-agent` 生成默认配置。
