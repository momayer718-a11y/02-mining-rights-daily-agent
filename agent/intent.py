from __future__ import annotations

import re
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class BriefIntent:
    topic: str
    commodity: str
    region: str | None
    intent: str
    days: int
    coverage_status: str
    missing_dimensions: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


COMMODITIES = {
    "lithium": ["锂", "lithium", "spodumene", "碳酸锂"],
    "copper": ["铜", "copper", "cu"],
    "nickel": ["镍", "nickel", "ni"],
    "zinc": ["锌", "zinc", "zn"],
    "iron ore": ["铁矿石", "iron ore"],
    "rare earth": ["稀土", "rare earth"],
    "cobalt": ["钴", "cobalt"],
    "gold": ["金", "gold", "au"],
    "uranium": ["铀", "uranium"],
    "graphite": ["石墨", "graphite"],
    "manganese": ["锰", "manganese"],
}

REGIONS = {
    "Pilbara": ["pilbara", "皮尔巴拉"],
    "Australia": ["澳洲", "澳大利亚", "australia"],
    "Peru": ["秘鲁", "peru"],
    "Indonesia": ["印尼", "印度尼西亚", "indonesia", "indonesian"],
    "China": ["中国", "china"],
    "DRC": ["刚果", "drc", "congo"],
    "Chile": ["智利", "chile"],
    "Canada": ["加拿大", "canada"],
    "USA": ["美国", "usa", "u.s."],
}

SUPPORTED_COMMODITIES = {"lithium", "copper", "nickel", "rare earth"}
LIMITED_COMMODITIES = {"zinc", "iron ore"}


def parse_brief_intent(prompt: str) -> BriefIntent:
    lowered = prompt.lower()
    commodity = _match(lowered, prompt, COMMODITIES) or "lithium"
    region = _match(lowered, prompt, REGIONS)
    days = _extract_days(prompt) or 7
    intent = _intent(lowered, prompt)
    topic = _topic(region, commodity)
    missing = []
    if commodity not in SUPPORTED_COMMODITIES:
        if commodity in LIMITED_COMMODITIES:
            missing.append(f"limited news coverage for {commodity}; loaded MCP cache lacks dedicated article evidence")
        else:
            missing.append(f"unsupported commodity: {commodity}")
    if region == "DRC" or commodity == "cobalt":
        missing.append("DRC/cobalt source not loaded")
    coverage = "supported" if not missing else "limited"
    return BriefIntent(topic=topic, commodity=commodity, region=region, intent=intent, days=days, coverage_status=coverage, missing_dimensions=sorted(set(missing)))


def _match(lowered: str, original: str, mapping: dict[str, list[str]]) -> str | None:
    for key, terms in mapping.items():
        if any(_contains_term(lowered, original, term) for term in terms):
            return key
    return None


def _contains_term(lowered: str, original: str, term: str) -> bool:
    if any("\u4e00" <= ch <= "\u9fff" for ch in term):
        return term in original
    if len(term) <= 2:
        return re.search(rf"(?<![a-z]){re.escape(term)}(?![a-z])", lowered) is not None
    return term in lowered


def _extract_days(text: str) -> int | None:
    match = re.search(r"近\s*(\d+)\s*天", text)
    if match:
        return int(match.group(1))
    if "今日" in text or "today" in text.lower():
        return 1
    return None


def _intent(lowered: str, original: str) -> str:
    if any(term in lowered or term in original for term in ["价格", "price", "trend", "走势"]):
        return "price"
    if any(term in lowered or term in original for term in ["政策", "policy", "quota", "traceability", "restriction"]):
        return "policy"
    if any(term in lowered or term in original for term in ["资源", "储量", "resource", "reserve"]):
        return "resources"
    if any(term in lowered or term in original for term in ["风险", "risk", "maintenance", "community", "water", "logistics"]):
        return "risk"
    return "daily"


def _topic(region: str | None, commodity: str) -> str:
    commodity_zh = {
        "lithium": "锂矿",
        "copper": "铜矿",
        "nickel": "镍矿",
        "zinc": "锌矿",
        "iron ore": "铁矿石",
        "rare earth": "稀土",
        "cobalt": "钴矿",
        "gold": "金矿",
        "uranium": "铀矿",
        "graphite": "石墨",
        "manganese": "锰矿",
    }[commodity]
    return f"{region} {commodity_zh}" if region else commodity_zh
