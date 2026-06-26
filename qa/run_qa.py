from __future__ import annotations

import json
import re
import statistics
import time
import os
from pathlib import Path

from agent.daily_brief import generate_brief_payload
from console.app import CONSOLE_HTML

PLACEHOLDERS = ["TODO", "placeholder", "Traceback", "undefined", "null null"]
REQUIRED_SECTIONS = ["一、执行摘要", "二、新闻摘要", "三、资源量 / 储量数据", "四、价格走势", "五、风险提示", "六、引用来源", "七、数据缺口"]
FORBIDDEN_OUTPUT = ["[ok]", "Executive Summary", "Data Gaps", "TODO", "placeholder", "Traceback"]


def run() -> dict:
    started = time.perf_counter()
    cases = json.loads(Path("qa/industry_cases.json").read_text(encoding="utf-8"))
    rows = []
    elapsed = []
    signatures = set()
    for case in cases:
        result = generate_brief_payload(case["prompt"])
        elapsed.append(result["elapsed_ms"])
        missing_sections = [section for section in REQUIRED_SECTIONS if section not in result["markdown"]]
        placeholder_hits = [token for token in FORBIDDEN_OUTPUT if token.lower() in result["markdown"].lower()]
        workflow_ok = _workflow_ok(result)
        signatures.add(_signature(result["markdown"]))
        rows.append(
            {
                "prompt": case["prompt"],
                "expected": case["expect_status"],
                "actual": result["status"],
                "passed": result["status"] == case["expect_status"] and not missing_sections and not placeholder_hits and workflow_ok,
                "elapsed_ms": result["elapsed_ms"],
                "warnings": result["warnings"],
                "missing_sections": missing_sections,
                "placeholder_hits": placeholder_hits,
                "workflow_ok": workflow_ok,
            }
        )
    frontend = _frontend_report(CONSOLE_HTML)
    backend = {
        "total": len(rows),
        "passed": sum(1 for row in rows if row["passed"]),
        "success_rate": round(sum(1 for row in rows if row["passed"]) / len(rows), 3),
        "avg_elapsed_ms": round(statistics.mean(elapsed), 2),
        "p95_elapsed_ms": round(sorted(elapsed)[int(len(elapsed) * 0.95) - 1], 2),
        "limited_rate": round(sum(1 for row in rows if row["actual"] == "limited") / len(rows), 3),
        "unique_brief_signatures": len(signatures),
        "rows": rows,
    }
    report = {"tool": "02-mining-rights-daily-agent", "status": "passed" if backend["passed"] == backend["total"] and frontend["passed"] else "failed", "elapsed_ms": round((time.perf_counter() - started) * 1000, 2), "frontend": frontend, "backend": backend}
    out_dir = Path(os.getenv("QA_REPORT_DIR", "outputs/generated/qa"))
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "qa_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "frontend_report.json").write_text(json.dumps(frontend, ensure_ascii=False, indent=2), encoding="utf-8")
    markdown = _markdown(report)
    Path(os.getenv("QA_REPORT_MD", "outputs/generated/QA_REPORT.md")).write_text(markdown, encoding="utf-8")
    if _truthy(os.getenv("QA_UPDATE_TRACKED_REPORTS", "")):
        tracked_dir = Path("qa/reports")
        tracked_dir.mkdir(parents=True, exist_ok=True)
        (tracked_dir / "qa_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        (tracked_dir / "frontend_report.json").write_text(json.dumps(frontend, ensure_ascii=False, indent=2), encoding="utf-8")
        Path("QA_REPORT.md").write_text(markdown, encoding="utf-8")
    if report["status"] != "passed":
        raise SystemExit(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report


def _frontend_report(html: str) -> dict:
    required = ["矿权日报 Agent 控制台", "简报主题", "Markdown 简报", "Agent 工作流画布", "Raw Tool Output", "后台工具 JSON 输出"]
    missing = [text for text in required if text not in html]
    placeholders = [token for token in PLACEHOLDERS if token.lower() in html.lower()]
    return {"passed": not missing and not placeholders, "missing": missing, "placeholder_hits": placeholders, "viewports": [{"width": 1280}, {"width": 768}, {"width": 390}]}


def _workflow_ok(result: dict) -> bool:
    names = {node.get("name") for node in result.get("workflow_trace", [])}
    required = {"用户输入", "Agent Planner", "mining-news-mcp", "mineral-pdf-mcp", "lme-price-mcp", "Brief Synthesizer", "Markdown Output"}
    return required.issubset(names)


def _signature(markdown: str) -> str:
    return re.sub(r"\s+", " ", markdown[:260]).strip()


def _truthy(value: str) -> bool:
    return value.lower() in {"1", "true", "yes", "on"}


def _markdown(report: dict) -> str:
    b = report["backend"]
    return (
        "# QA_REPORT - Mining Rights Daily Agent\n\n"
        f"- Status: {report['status']}\n"
        f"- Backend cases: {b['passed']}/{b['total']}\n"
        f"- Avg elapsed: {b['avg_elapsed_ms']} ms\n"
        f"- P95 elapsed: {b['p95_elapsed_ms']} ms\n"
        f"- Limited rate: {b['limited_rate']}\n"
        f"- Unique brief signatures: {b['unique_brief_signatures']}\n"
        f"- Frontend passed: {report['frontend']['passed']}\n"
    )


if __name__ == "__main__":
    run()
