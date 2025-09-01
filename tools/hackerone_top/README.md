# HackerOne Top Programs Tool

Scrapes HackerOne Hacktivity for a given month, aggregates disclosed bounty payouts by program, and outputs results to the Bastet `logs/` directory.

## Virtualenv

This tool runs in its own virtual environment to isolate dependencies.

```bash
# Activate venv
. tools/hackerone_top/venv/bin/activate

# Run for August 2025 and show top 10
python tools/hackerone_top/scraper.py --month 2025-08 --top 10
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

- Only disclosed reports with visible bounty amounts are considered.
- Selectors are resilient but may require updates if HackerOne changes markup.
- No authentication is used.


