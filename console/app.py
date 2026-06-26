from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from agent.daily_brief import generate_brief_payload
from agent.intent import parse_brief_intent
from tools.news import fetch_article, search
from tools.pdf_extract import extract_resources
from tools.prices import get_price, get_trend


class BriefRequest(BaseModel):
    prompt: str = "给我生成一份关于 Pilbara 锂矿的今日简报"


app = FastAPI(title="Mining Rights Daily Agent Console")


@app.get("/", response_class=HTMLResponse)
def console() -> str:
    return CONSOLE_HTML


@app.get("/health")
def health() -> dict:
    return {"ok": True, "status": "ok", "service": "mining-rights-daily-agent", "warnings": [], "source_mode": "service", "data_quality": {"grade": "service"}, "elapsed_ms": 0}


@app.get("/tools")
def tools() -> dict:
    return {
        "mcp_servers": [
            {"name": "mining-news-mcp", "tools": ["search(query, days)", "fetch_article(url)"]},
            {"name": "mineral-pdf-mcp", "tools": ["extract_resources(pdf_url)"]},
            {"name": "lme-price-mcp", "tools": ["get_price(commodity, date)", "get_trend(commodity, days)"]},
        ]
    }


@app.post("/brief")
def brief(payload: BriefRequest) -> dict:
    result = generate_brief_payload(payload.prompt)
    out = Path("outputs/pilbara_daily.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(result["markdown"], encoding="utf-8")
    return {**result, "output": str(out)}


@app.get("/news")
def news(query: str = "Pilbara lithium", days: int | None = None) -> dict:
    effective_days = days or parse_brief_intent(query).days
    rows = search(query, effective_days)
    warnings = [] if rows else ["no relevant news evidence found"]
    return {"status": "ok" if rows else "limited", "query": query, "days": effective_days, "results": rows, "articles": [fetch_article(row["url"]) for row in rows[:3]], "warnings": warnings, "source_mode": "fixture", "data_quality": {"grade": "usable" if rows else "limited", "result_count": len(rows)}, "elapsed_ms": 0}


@app.get("/resources")
def resources(pdf_url: str = "fixture://pilbara-technical-report") -> dict:
    return extract_resources(pdf_url)


@app.get("/prices")
def prices(commodity: str = "lithium", days: int | None = None) -> dict:
    effective_days = days or parse_brief_intent(commodity).days
    latest = get_price(commodity)
    trend = get_trend(commodity, effective_days)
    status = "ok" if trend.get("status") == "ok" else "limited"
    return {"status": status, "days": effective_days, "latest": latest, "trend": trend, "warnings": sorted(set(latest.get("warnings", []) + trend.get("warnings", []))), "source_mode": latest.get("source", "none"), "data_quality": {"grade": "usable" if status == "ok" else "limited"}, "elapsed_ms": 0}


CONSOLE_HTML = """
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Mining Rights Daily Agent</title>
  <style>
    :root { --bg:#f5f7fb; --panel:#fff; --ink:#172033; --muted:#65758b; --line:#d8e0ea; --accent:#1d4ed8; --green:#047857; }
    * { box-sizing:border-box; }
    body { margin:0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif; background:var(--bg); color:var(--ink); }
    header { background:#fff; border-bottom:1px solid var(--line); padding:24px 32px 16px; }
    h1 { margin:0 0 6px; font-size:24px; letter-spacing:0; }
    main { max-width:1220px; margin:0 auto; padding:24px 32px 36px; display:grid; gap:16px; }
    .layout { display:grid; grid-template-columns:360px minmax(0,1fr); gap:16px; align-items:start; }
    .panel { background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:16px; }
    .cards { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; }
    .card { border:1px solid var(--line); border-radius:8px; padding:13px; background:#fbfdff; }
    label { display:block; font-weight:700; margin-bottom:8px; }
    textarea, input { width:100%; border:1px solid var(--line); border-radius:6px; padding:10px; font:inherit; }
    textarea { min-height:112px; resize:vertical; }
    button { border:0; border-radius:6px; background:var(--accent); color:#fff; font-weight:700; padding:10px 14px; cursor:pointer; }
    button.secondary { background:#334155; }
    button:disabled { opacity:.62; cursor:not-allowed; }
    .row { display:flex; gap:10px; flex-wrap:wrap; align-items:center; }
    .muted { color:var(--muted); font-size:13px; }
    .field-grid { display:grid; grid-template-columns:1fr 92px; gap:10px; }
    .workflow { display:grid; grid-template-columns:repeat(7,minmax(120px,1fr)); gap:10px; align-items:stretch; }
    .node { position:relative; border:1px solid var(--line); border-radius:8px; padding:12px; background:#fbfdff; cursor:pointer; min-height:96px; }
    .node::after { content:""; position:absolute; top:50%; right:-10px; width:10px; border-top:2px solid #94a3b8; }
    .node:last-child::after { display:none; }
    .node b { display:block; font-size:14px; margin-bottom:6px; }
    .node .status { display:inline-block; border-radius:999px; padding:2px 8px; font-size:12px; font-weight:700; background:#e2e8f0; color:#334155; }
    .node.done .status { background:#dcfce7; color:#166534; }
    .node.limited .status { background:#fef3c7; color:#92400e; }
    .node.failed .status { background:#fee2e2; color:#991b1b; }
    details { border:1px solid var(--line); border-radius:8px; background:#fff; }
    summary { cursor:pointer; padding:12px 14px; font-weight:750; color:#1d4ed8; }
    details[open] summary { border-bottom:1px solid var(--line); }
    .details-body { padding:14px; }
    pre { margin:0; white-space:pre-wrap; overflow:auto; background:#101827; color:#e5e7eb; border-radius:8px; padding:14px; font-size:13px; line-height:1.45; }
    .brief { min-height:520px; }
    @media (max-width:1080px) { .workflow { grid-template-columns:repeat(2,minmax(0,1fr)); } .node::after { display:none; } }
    @media (max-width:860px) { header, main { padding-left:16px; padding-right:16px; } .layout { grid-template-columns:1fr; } .cards { grid-template-columns:1fr; } }
    @media (max-width:520px) { .field-grid { grid-template-columns:1fr; } }
  </style>
</head>
<body>
  <header>
    <h1>矿权日报 Agent 控制台</h1>
    <div class="muted">3 个 MCP server 工具 + Agent 编排 + Markdown 简报</div>
  </header>
  <main>
    <section class="cards">
      <div class="card"><b>mining-news-mcp</b><div class="muted">search · fetch_article</div></div>
      <div class="card"><b>mineral-pdf-mcp</b><div class="muted">extract_resources</div></div>
      <div class="card"><b>lme-price-mcp</b><div class="muted">get_price · get_trend</div></div>
    </section>
    <section class="panel">
      <label>Agent 工作流画布</label>
      <div id="workflow" class="workflow">
        <div class="muted">等待生成简报...</div>
      </div>
    </section>
    <section class="layout">
      <div class="panel">
        <label for="prompt">简报主题</label>
        <textarea id="prompt">给我生成一份关于 Pilbara 锂矿的今日简报</textarea>
        <div class="row" style="margin-top:10px">
          <button id="briefBtn" onclick="brief()">生成简报</button>
          <button id="toolsBtn" class="secondary" onclick="loadTools()">工具清单</button>
        </div>
        <hr style="border:0;border-top:1px solid var(--line);margin:16px 0">
        <label>工具探针</label>
        <div>
          <input id="newsQuery" value="Pilbara lithium" aria-label="News query">
        </div>
        <div style="margin-top:10px">
          <input id="commodity" value="lithium" aria-label="Commodity">
        </div>
        <div class="row">
          <button id="newsBtn" class="secondary" onclick="probeNews()">新闻</button>
          <button id="resourcesBtn" class="secondary" onclick="probeResources()">储量</button>
          <button id="pricesBtn" class="secondary" onclick="probePrices()">价格</button>
        </div>
      </div>
      <div class="panel">
        <label>Markdown 简报</label>
        <pre id="briefOut" class="brief">等待生成...</pre>
      </div>
    </section>
    <section class="panel">
      <details>
        <summary>Raw Tool Output（后台工具 JSON 输出）</summary>
        <div class="details-body">
          <div class="muted" style="margin-bottom:8px">这里展示 MCP 工具链和 Agent 返回的完整 JSON，用于调试、审计和复现；正常阅读日报时可保持折叠。</div>
          <pre id="raw">等待操作...</pre>
        </div>
      </details>
    </section>
  </main>
  <script>
    async function json(url, options={}) { const res = await fetch(url, options); return await res.json(); }
    function setBusy(button, busy, text) {
      button.disabled = busy;
      if (busy) {
        button.dataset.label = button.textContent;
        button.textContent = text;
      } else if (button.dataset.label) {
        button.textContent = button.dataset.label;
      }
    }
    async function brief() {
      setBusy(briefBtn, true, '生成中...');
      try {
        briefOut.textContent = '正在调用新闻、资源与价格工具生成简报...';
        const data = await json('/brief', {method:'POST', headers:{'content-type':'application/json'}, body:JSON.stringify({prompt:document.getElementById('prompt').value})});
        briefOut.textContent = data.markdown;
        renderWorkflow(data.workflow_trace || []);
        raw.textContent = JSON.stringify(data, null, 2);
      } finally {
        setBusy(briefBtn, false);
      }
    }
    async function loadTools() {
      setBusy(toolsBtn, true, '加载中...');
      try {
        const data = await json('/tools');
        raw.textContent = JSON.stringify(data, null, 2);
      } finally {
        setBusy(toolsBtn, false);
      }
    }
    async function probeNews() {
      setBusy(newsBtn, true, '查询中...');
      try {
        const data = await json(`/news?query=${encodeURIComponent(document.getElementById('newsQuery').value)}`);
        raw.textContent = JSON.stringify(data, null, 2);
      } finally {
        setBusy(newsBtn, false);
      }
    }
    async function probeResources() {
      setBusy(resourcesBtn, true, '抽取中...');
      try {
        const data = await json('/resources');
        raw.textContent = JSON.stringify(data, null, 2);
      } finally {
        setBusy(resourcesBtn, false);
      }
    }
    async function probePrices() {
      setBusy(pricesBtn, true, '查询中...');
      try {
        const data = await json(`/prices?commodity=${encodeURIComponent(document.getElementById('commodity').value)}`);
        raw.textContent = JSON.stringify(data, null, 2);
      } finally {
        setBusy(pricesBtn, false);
      }
    }
    function renderWorkflow(trace) {
      workflow.innerHTML = trace.length ? trace.map((node, index) => {
        const status = node.status || 'pending';
        return `<div class="node ${escapeHtml(status)}" onclick="showNode(${index})"><b>${escapeHtml(node.name)}</b><div class="status">${escapeHtml(status)}</div><div class="muted" style="margin-top:8px">${escapeHtml(node.tool)}</div><div class="muted">${escapeHtml(node.elapsed_ms)} ms</div></div>`;
      }).join('') : '<div class="muted">暂无工作流记录。</div>';
      window.currentTrace = trace;
    }
    function showNode(index) {
      const node = (window.currentTrace || [])[index];
      if (node) raw.textContent = JSON.stringify(node, null, 2);
    }
    function escapeHtml(value) {
      return String(value || '').replace(/[&<>"']/g, (ch) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
    }
    brief();
  </script>
</body>
</html>
"""
