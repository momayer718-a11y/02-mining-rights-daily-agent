# 02 - Mining Rights Daily Agent MVP

对应题 #2：基于 MCP 协议的“矿权日报 Agent”。

包含三个独立 MCP server：

- `mining-news-mcp`: `search(query, days)`, `fetch_article(url)`
- `mineral-pdf-mcp`: `extract_resources(pdf_url)`
- `lme-price-mcp`: `get_price(commodity, date)`, `get_trend(commodity, days)`

Agent client 输入：

```text
给我生成一份关于 Pilbara 锂矿的今日简报
```

输出中文 Markdown 简报：新闻摘要、储量数据、价格走势、风险提示、引用链接和数据缺口。

```bash
make brief
docker compose up --build
```

Web 控制台：

```bash
make console
# open http://localhost:8002
```

行业级验收：

```bash
make test
make qa
make package
```

简报固定输出 `一、执行摘要 / 二、新闻摘要 / 三、资源量 / 储量数据 / 四、价格走势 / 五、风险提示 / 六、引用来源 / 七、数据缺口`。不支持的 commodity 会返回 `limited` 和 warning，不会静默降级到 lithium。

Web 控制台包含 Agent 工作流画布：用户输入、Planner、3 个 MCP server、Brief Synthesizer、Markdown Output。每个节点有状态、耗时和摘要，Raw Tool Output 默认折叠。

可选模型增强：

```bash
cp .env.example .env
export APIMART_API_KEY=...
export APIMART_MODEL=gemini-3.5-flash
```

有 APIMart key 时使用 Gemini 生成中文简报；无 key 或模型失败时使用中文模板 fallback，demo 仍可运行。真实密钥不得写入项目文件或 zip。
