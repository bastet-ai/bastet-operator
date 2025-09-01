# HackerOne Top Programs Tool

Scrapes HackerOne Hacktivity for a given month, aggregates disclosed bounty payouts by program, and outputs results to the Bastet `logs/` directory.

## Virtualenv

This tool runs in its own virtual environment to isolate dependencies.

```bash
# Activate venv
. tools/hackerone_top/venv/bin/activate

# Run for August 2025 and show top 10 (non-headless with slow-mo)
python tools/hackerone_top/scraper.py --month 2025-08 --top 10 --no-headless --slow-mo 250
```

## Outputs

- logs/tool_outputs/hackerone_payouts_YYYY-MM_<timestamp>_raw.json
- logs/findings/hackerone_payouts_YYYY-MM_<timestamp>_agg.csv

## Dependencies

- playwright
- pandas
- typer
- rich
- pydantic

Install and browser setup (already done when scaffolding):

```bash
. tools/hackerone_top/venv/bin/activate
pip install --upgrade pip
pip install playwright pandas pydantic typer rich
python -m playwright install --with-deps chromium
```

## Notes
- API Mode (recommended):

```bash
export H1_USERNAME="<your_username>"
export H1_API_TOKEN="<your_token>"

# Run via API for August 2025
tools/hackerone_top/run_api.sh 2025-08

# Or directly
. tools/hackerone_top/venv/bin/activate
pip install requests pandas typer
python tools/hackerone_top/api_client.py --month 2025-08 --top 10
```

- The API uses Lucene-style filters like:
  `disclosed_at:[2025-08-01 TO 2025-09-01) total_awarded_amount:>0`
- Rate limits apply (~600 req/min); pagination handled via `page[cursor]`.

- Only disclosed reports with visible bounty amounts are considered.
- Selectors are resilient but may require updates if HackerOne changes markup.
- No authentication is used.


