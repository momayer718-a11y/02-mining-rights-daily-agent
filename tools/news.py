from __future__ import annotations

from datetime import date, timedelta

NEWS = [
    {
        "title": "Pilbara Minerals flags stronger spodumene shipments",
        "url": "https://fixture.local/news/pilbara-spodumene-shipments",
        "published_at": (date.today() - timedelta(days=1)).isoformat(),
        "summary": "Pilbara lithium operations reported better concentrate shipments while warning that port scheduling and price volatility remain key risks.",
        "body": "Pilbara Minerals continues to optimize spodumene concentrate shipments. Management highlighted stronger logistics execution, but noted lithium price weakness and permitting timelines as watch items.",
    },
    {
        "title": "Australia expands critical minerals financing",
        "url": "https://fixture.local/news/australia-critical-minerals-financing",
        "published_at": (date.today() - timedelta(days=2)).isoformat(),
        "summary": "Australia's critical minerals policy support now emphasizes export finance, downstream processing grants and offtake partnerships.",
        "body": "The latest policy direction supports lithium, nickel and rare earth projects through financing, downstream refining incentives and strategic partnerships rather than direct export restrictions.",
    },
    {
        "title": "Lithium market watches battery restocking",
        "url": "https://fixture.local/news/lithium-battery-restocking",
        "published_at": (date.today() - timedelta(days=3)).isoformat(),
        "summary": "Battery restocking has stabilized lithium carbonate prices, but project economics remain sensitive to concentrate discounts.",
        "body": "Lithium buyers are rebuilding inventories. The price recovery is uneven and miners remain exposed to spodumene concentrate discounts and conversion capacity.",
    },
    {
        "title": "Copper projects monitor community and water risk in Peru and Chile",
        "url": "https://fixture.local/news/copper-community-water-risk",
        "published_at": (date.today() - timedelta(days=4)).isoformat(),
        "summary": "Copper developers continue to monitor community agreements, water access and concentrator maintenance risk in Latin America.",
        "body": "Peru and Chile copper projects face recurring social license, water and maintenance risks. This fixture is limited and should be replaced with primary company filings for investment use.",
    },
    {
        "title": "Indonesia nickel policy keeps export and refining risk in focus",
        "url": "https://fixture.local/news/indonesia-nickel-policy",
        "published_at": (date.today() - timedelta(days=5)).isoformat(),
        "summary": "Nickel investors are watching Indonesian refining capacity, quota policy and export restrictions.",
        "body": "Indonesia nickel supply remains sensitive to quota approval, smelter margins and battery demand. Export policy risk is material for laterite supply chains.",
    },
    {
        "title": "China rare earth traceability and quota supervision tighten",
        "url": "https://fixture.local/news/china-rare-earth-quota",
        "published_at": (date.today() - timedelta(days=6)).isoformat(),
        "summary": "Rare earth policy attention remains on traceability, quotas, environmental checks and consolidation.",
        "body": "China rare earth supply chain supervision emphasizes quota discipline, traceability and environmental compliance.",
    },
]


def search(query: str, days: int = 7) -> list[dict]:
    lowered = query.lower()
    cutoff = date.today() - timedelta(days=days)
    rows = []
    for item in NEWS:
        published = date.fromisoformat(item["published_at"])
        blob = f"{item['title']} {item['summary']} {item['body']}".lower()
        score = _score(lowered, blob)
        if published >= cutoff and score > 0:
            row = {k: item[k] for k in ["title", "url", "published_at", "summary"]}
            row["relevance"] = score
            rows.append(row)
    rows.sort(key=lambda row: row["relevance"], reverse=True)
    return rows


def fetch_article(url: str) -> dict:
    for item in NEWS:
        if item["url"] == url:
            return item
    return {"title": "Unknown article", "url": url, "published_at": date.today().isoformat(), "summary": "", "body": "Article not found in fixture cache."}


def _score(query: str, blob: str) -> int:
    synonyms = {
        "pilbara": ["pilbara", "spodumene", "lithium"],
        "lithium": ["lithium", "spodumene"],
        "copper": ["copper", "peru", "chile"],
        "peru": ["peru", "community"],
        "indonesia": ["indonesia", "nickel"],
        "nickel": ["nickel", "indonesian", "laterite"],
        "rare": ["rare earth", "quota", "traceability"],
        "china": ["china", "rare earth"],
        "drc": ["drc", "cobalt"],
        "cobalt": ["cobalt"],
    }
    score = 0
    for term in query.split():
        if term in blob:
            score += 2
    for needle, terms in synonyms.items():
        if needle in query and any(term in blob for term in terms):
            score += 3
    return score
