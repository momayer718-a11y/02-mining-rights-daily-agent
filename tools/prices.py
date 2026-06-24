from __future__ import annotations

import re
from datetime import date, timedelta

BASE = {
    "lithium": 102500.0,
    "copper": 9750.0,
    "zinc": 2850.0,
    "nickel": 18200.0,
    "iron ore": 112.0,
    "rare earth": 68000.0,
}


def get_price(commodity: str, date_value: str | None = None) -> dict:
    key = _normalize(commodity)
    if key not in BASE:
        return {
            "status": "unsupported",
            "commodity": commodity,
            "date": date_value or date.today().isoformat(),
            "price": None,
            "unit": None,
            "source": "none",
            "warnings": [f"unsupported commodity: {commodity}"],
        }
    date_value = date_value or date.today().isoformat()
    base = BASE[key]
    offset = sum(ord(ch) for ch in date_value) % 9 - 4
    return {
        "commodity": key,
        "date": date_value,
        "price": round(base * (1 + offset / 100), 2),
        "unit": "USD/t" if key != "iron ore" else "USD/dmt",
        "source": "fixture://price-cache",
        "status": "ok",
        "warnings": ["fixture price cache; replace with licensed market feed for production"],
    }


def get_trend(commodity: str, days: int = 7) -> dict:
    key = _normalize(commodity)
    if key not in BASE:
        return {"status": "unsupported", "commodity": commodity, "days": days, "direction": "unknown", "change_pct": None, "points": [], "warnings": [f"unsupported commodity: {commodity}"]}
    points = []
    for idx in range(days):
        current = date.today() - timedelta(days=days - idx - 1)
        points.append(get_price(key, current.isoformat()))
    first = points[0]["price"]
    last = points[-1]["price"]
    direction = "up" if last > first else "down" if last < first else "flat"
    return {"status": "ok", "commodity": key, "days": days, "direction": direction, "change_pct": round((last - first) / first * 100, 2), "points": points, "warnings": ["fixture price cache; replace with licensed market feed for production"]}


def _normalize(value: str) -> str:
    lowered = value.lower()
    tokens = set(re.findall(r"[a-z]+", lowered))
    if "cu" in tokens or "copper" in tokens or "铜" in value:
        return "copper"
    if "zn" in tokens or "zinc" in tokens or "锌" in value:
        return "zinc"
    if "ni" in tokens or "nickel" in tokens or "镍" in value:
        return "nickel"
    if "iron" in lowered or "铁" in value:
        return "iron ore"
    if "rare" in lowered or "稀土" in value:
        return "rare earth"
    if "lithium" in lowered or "li" == lowered.strip() or "锂" in value:
        return "lithium"
    return lowered.strip()
