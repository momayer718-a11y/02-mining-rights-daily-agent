from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from tools.pdf_extract import extract_resources as extract_resources_impl

mcp = FastMCP("mineral-pdf-mcp")


@mcp.tool()
def extract_resources(pdf_url: str) -> dict:
    """Extract Indicated and Inferred resources from a NI 43-101 style report."""
    return extract_resources_impl(pdf_url)


if __name__ == "__main__":
    mcp.run()

