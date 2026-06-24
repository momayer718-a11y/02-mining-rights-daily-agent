from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from tools.prices import get_price as get_price_impl
from tools.prices import get_trend as get_trend_impl

mcp = FastMCP("lme-price-mcp")


@mcp.tool()
def get_price(commodity: str, date: str | None = None) -> dict:
    """Get commodity price for a date."""
    return get_price_impl(commodity, date)


@mcp.tool()
def get_trend(commodity: str, days: int = 7) -> dict:
    """Get commodity price trend."""
    return get_trend_impl(commodity, days)


if __name__ == "__main__":
    mcp.run()

