from __future__ import annotations

import pytest

from agent.daily_brief import generate_brief, generate_brief_payload
from tools.news import fetch_article, search
from tools.pdf_extract import extract_resources
from tools.prices import get_price, get_trend


@pytest.fixture(autouse=True)
def disable_live_model(monkeypatch) -> None:
    monkeypatch.setenv("MODEL_API_KEY", "")
    monkeypatch.setenv("MODEL_KEY_PASSPHRASE", "")
    monkeypatch.setattr("agent.daily_brief.complete_json", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        "agent.daily_brief.model_metadata",
        lambda: {"model_provider": "fallback", "model_name": "deterministic-template", "model_mode": "fallback", "model_reasoning": "not_requested"},
    )


def test_news_tools() -> None:
    rows = search("Pilbara lithium", 7)
    assert rows
    article = fetch_article(rows[0]["url"])
    assert "body" in article


def test_pdf_tool() -> None:
    result = extract_resources("fixture://pilbara")
    assert len(result["resources"]) == 2
    assert result["resources"][0]["category"] == "Indicated"


def test_price_tools() -> None:
    price = get_price("lithium", "2026-06-23")
    trend = get_trend("lithium", 7)
    assert price["price"] > 0
    assert len(trend["points"]) == 7


def test_agent_brief() -> None:
    brief = generate_brief("给我生成一份关于 Pilbara 锂矿的今日简报")
    assert "# Pilbara 锂矿今日简报" in brief
    assert "一、执行摘要" in brief
    assert "二、新闻摘要" in brief
    assert "三、资源量 / 储量数据" in brief
    assert "四、价格走势" in brief
    assert "五、风险提示" in brief
    assert "六、引用来源" in brief
    assert "七、数据缺口" in brief
    assert not brief.startswith("[ok]")


def test_unknown_commodity_does_not_fallback_to_lithium() -> None:
    payload = generate_brief_payload("给我生成一份关于 DRC cobalt 的今日简报")
    assert payload["status"] == "limited"
    assert payload["commodity"] == "cobalt"
    assert "unsupported" in " ".join(payload["warnings"])


def test_workflow_trace_and_topic_variation() -> None:
    lithium = generate_brief_payload("给我生成一份关于 Pilbara 锂矿的今日简报")
    nickel = generate_brief_payload("给我生成一份关于 Indonesia nickel 的今日简报")
    names = [node["name"] for node in lithium["workflow_trace"]]
    assert "Agent Planner" in names
    assert "mining-news-mcp" in names
    assert "mineral-pdf-mcp" in names
    assert "lme-price-mcp" in names
    assert lithium["markdown"] != nickel["markdown"]
    assert nickel["commodity"] == "nickel"
