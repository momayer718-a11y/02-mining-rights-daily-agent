from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from tools.news import fetch_article as fetch_article_impl
from tools.news import search as search_impl

mcp = FastMCP("mining-news-mcp")


@mcp.tool()
def search(query: str, days: int = 7) -> list[dict]:
    """Search recent mining news."""
    return search_impl(query, days)


@mcp.tool()
def fetch_article(url: str) -> dict:
    """Fetch an article by URL."""
    return fetch_article_impl(url)


if __name__ == "__main__":
    mcp.run()

