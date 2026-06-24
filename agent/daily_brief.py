from __future__ import annotations

import argparse
import time
from pathlib import Path

from agent.intent import BriefIntent, parse_brief_intent
from agent.model_client import complete_json, model_metadata
from tools.news import fetch_article, search
from tools.pdf_extract import extract_resources
from tools.prices import get_price, get_trend


def generate_brief(prompt: str) -> str:
    return generate_brief_payload(prompt)["markdown"]


def generate_brief_payload(prompt: str) -> dict:
    started = time.perf_counter()
    trace = []
    intent = parse_brief_intent(prompt)
    trace.append(_node("用户输入", "input", "done", f"收到主题：{prompt}", 0, []))
    trace.append(_node("Agent Planner", "planner", "done", f"识别为 {intent.topic} / {intent.commodity} / {intent.intent}", 0, intent.missing_dimensions))

    news_started = time.perf_counter()
    news = search(_news_query(intent), days=max(intent.days, 7))
    articles = [fetch_article(item["url"]) for item in news[:3]]
    news_warnings = [] if articles else ["no relevant news evidence found"]
    trace.append(_node("mining-news-mcp", "search + fetch_article", "done" if articles else "limited", f"返回 {len(articles)} 篇新闻证据", news_started, news_warnings))

    resource_started = time.perf_counter()
    resources = extract_resources("fixture://pilbara-technical-report")
    trace.append(_node("mineral-pdf-mcp", "extract_resources", "done", f"抽取 {len(resources.get('resources', []))} 条资源量记录", resource_started, []))

    price_started = time.perf_counter()
    latest = get_price(intent.commodity)
    trend = get_trend(intent.commodity, days=7)
    price_warnings = sorted(set(latest.get("warnings", []) + trend.get("warnings", [])))
    if trend.get("status") == "unsupported":
        price_warnings.append("price trend unsupported; no silent fallback applied")
    trace.append(_node("lme-price-mcp", "get_price + get_trend", "done" if trend.get("status") == "ok" else "limited", _price_summary_zh(intent.commodity, latest, trend), price_started, price_warnings))

    warnings = sorted(set(intent.missing_dimensions + news_warnings + price_warnings))
    if intent.coverage_status == "limited" and intent.commodity in {"zinc", "iron ore"}:
        warnings.append(f"limited news coverage for {intent.commodity}; loaded MCP cache lacks dedicated article evidence")
    status = "ok" if articles and trend.get("status") == "ok" and not intent.missing_dimensions else "limited"

    synth_started = time.perf_counter()
    markdown = _model_markdown(prompt, intent, articles, resources, latest, trend, warnings)
    if not markdown:
        markdown = _render_markdown(intent, articles, resources, latest, trend, warnings)
    trace.append(_node("Brief Synthesizer", "model/fallback markdown", "done" if markdown else "failed", "生成中文 Markdown 简报", synth_started, []))
    trace.append(_node("Markdown Output", "render", "done", "简报已输出到控制台和 outputs/pilbara_daily.md", 0, []))

    return {
        "status": status,
        "prompt": prompt,
        "intent": intent.to_dict(),
        "topic": intent.topic,
        "commodity": intent.commodity,
        "markdown": markdown,
        "workflow_trace": trace,
        "warnings": sorted(set(warnings)),
        "source_mode": "fixture",
        "data_quality": {"grade": "usable" if status == "ok" else "limited", "news_count": len(articles), "price_status": trend.get("status")},
        "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
        **model_metadata(),
    }


def _model_markdown(prompt: str, intent: BriefIntent, articles: list[dict], resources: dict, latest: dict, trend: dict, warnings: list[str]) -> str | None:
    payload = complete_json(
        "你是矿业日报 Agent。只基于输入工具结果生成中文 Markdown。必须包含：一、执行摘要；二、新闻摘要；三、资源量 / 储量数据；四、价格走势；五、风险提示；六、引用来源；七、数据缺口。输出 JSON: markdown:string。",
        {
            "prompt": prompt,
            "intent": intent.to_dict(),
            "articles": articles,
            "resources": resources,
            "latest": latest,
            "trend": trend,
            "warnings": warnings,
        },
    )
    if isinstance(payload, dict) and isinstance(payload.get("markdown"), str) and "一、执行摘要" in payload["markdown"]:
        return payload["markdown"].strip() + "\n"
    return None


def _render_markdown(intent: BriefIntent, articles: list[dict], resources: dict, latest: dict, trend: dict, warnings: list[str]) -> str:
    lines = [
        f"# {intent.topic}今日简报",
        "",
        "## 一、执行摘要",
        f"- 主题：{intent.topic}",
        f"- 矿种：{_commodity_zh(intent.commodity)}",
        f"- 覆盖状态：{'可用' if not warnings else '有限'}",
        f"- 结论：当前简报基于新闻、资源量和价格工具生成；若数据缺口存在，结论只作方向性参考。",
        "",
        "## 二、新闻摘要",
    ]
    if articles:
        for idx, item in enumerate(articles, start=1):
            lines.append(f"- [{idx}] **{item['title']}**（{item['published_at']}）：{_zh_news_summary(item, intent)}")
    else:
        lines.append("- 未在已加载新闻缓存中找到直接相关新闻。")
    lines.extend(["", "## 三、资源量 / 储量数据"])
    for row in resources.get("resources", []):
        lines.append(f"- {row['category']}：矿石量 {row['ore_mt']} Mt，品位 {row['grade']} {row['grade_unit']}，金属量 {row['metal']} {row['metal_unit']}。来源：{row['source']}")
    lines.extend(["", "## 四、价格走势"])
    if trend.get("status") == "ok":
        lines.append(f"- {_commodity_zh(intent.commodity)}近 {trend['days']} 天方向：{_direction_zh(trend['direction'])}，变动 {trend['change_pct']}%。")
        lines.append(f"- 最新价格：{latest['price']} {latest['unit']}，来源：{latest['source']}。")
    else:
        lines.append(f"- 暂无可用价格趋势：{'; '.join(trend.get('warnings', []))}")
    lines.extend(["", "## 五、风险提示"])
    for risk in _risks(intent, warnings):
        lines.append(f"- {risk}")
    lines.extend(["", "## 六、引用来源"])
    for item in articles:
        lines.append(f"- {item['url']}")
    lines.append(f"- {resources.get('pdf_url', 'fixture://pilbara-technical-report')}")
    if latest.get("source") and latest.get("source") != "none":
        lines.append(f"- {latest['source']}")
    lines.extend(["", "## 七、数据缺口"])
    if warnings:
        for warning in sorted(set(warnings)):
            lines.append(f"- {warning}")
    else:
        lines.append("- 当前 demo 缓存未发现阻断性数据缺口；正式使用仍应替换授权新闻、PDF 和行情源。")
    return "\n".join(lines) + "\n"


def _node(name: str, tool: str, status: str, summary: str, started: float, warnings: list[str]) -> dict:
    elapsed = 0 if not started else round((time.perf_counter() - started) * 1000, 2)
    return {"name": name, "tool": tool, "status": status, "elapsed_ms": elapsed, "summary": summary, "warnings": warnings}


def _news_query(intent: BriefIntent) -> str:
    return " ".join(part for part in [intent.region, intent.commodity] if part)


def _price_summary_zh(commodity: str, latest: dict, trend: dict) -> str:
    if trend.get("status") != "ok":
        return f"{_commodity_zh(commodity)}价格趋势不可用"
    return f"{_commodity_zh(commodity)}价格{_direction_zh(trend['direction'])}，最新 {latest.get('price')} {latest.get('unit')}"


def _zh_news_summary(item: dict, intent: BriefIntent) -> str:
    return f"该新闻与{intent.topic}相关，原文摘要为：{item.get('summary', '')}"


def _risks(intent: BriefIntent, warnings: list[str]) -> list[str]:
    risks = ["价格、政策、物流、社区许可和数据覆盖范围均需要在投资使用前复核。"]
    if intent.commodity == "lithium":
        risks.append("锂矿需关注电池补库、锂辉石折扣、转化产能和港口排期。")
    if intent.commodity == "nickel":
        risks.append("镍矿需关注印尼配额审批、冶炼利润和电池需求。")
    if intent.commodity == "copper":
        risks.append("铜矿需关注社区协议、水资源、维护停产和库存变化。")
    if intent.commodity == "rare earth":
        risks.append("稀土需关注配额、追溯、环保合规和供应链集中度。")
    if warnings:
        risks.append("本次简报存在数据缺口，相关结论应按有限证据处理。")
    return risks


def _commodity_zh(commodity: str) -> str:
    return {
        "lithium": "锂",
        "copper": "铜",
        "nickel": "镍",
        "zinc": "锌",
        "iron ore": "铁矿石",
        "rare earth": "稀土",
        "cobalt": "钴",
        "gold": "金",
        "uranium": "铀",
        "graphite": "石墨",
        "manganese": "锰",
    }.get(commodity, commodity)


def _direction_zh(direction: str) -> str:
    return {"up": "上行", "down": "下行", "flat": "持平", "unknown": "未知"}.get(direction, direction)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt")
    parser.add_argument("--out", default="")
    args = parser.parse_args()
    brief = generate_brief_payload(args.prompt)["markdown"]
    if args.out:
        path = Path(args.out)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(brief, encoding="utf-8")
    print(brief)


if __name__ == "__main__":
    main()
