.PHONY: brief console test qa package mcp-news mcp-pdf mcp-price

brief:
	python3 -m agent.daily_brief "给我生成一份关于 Pilbara 锂矿的今日简报" --out outputs/pilbara_daily.md

console:
	uvicorn console.app:app --host 0.0.0.0 --port 8002

test:
	PYTHONPATH=. pytest -q

qa:
	PYTHONPATH=. python3 -m qa.run_qa

package:
	rm -f /Users/Zhuanz/Desktop/02-mining-rights-daily-agent-tool.zip
	cd .. && zip -qr /Users/Zhuanz/Desktop/02-mining-rights-daily-agent-tool.zip 02-mining-rights-daily-agent -x '02-mining-rights-daily-agent/.git/*' '02-mining-rights-daily-agent/.env' '02-mining-rights-daily-agent/.env.local' '02-mining-rights-daily-agent/.venv/*' '02-mining-rights-daily-agent/.pytest_cache/*' '02-mining-rights-daily-agent/**/__pycache__/*' '02-mining-rights-daily-agent/outputs/*.log'

mcp-news:
	python3 -m servers.mining_news_mcp

mcp-pdf:
	python3 -m servers.mineral_pdf_mcp

mcp-price:
	python3 -m servers.lme_price_mcp
