#!/usr/bin/env python3
"""
HackerOne Program Payout Aggregator (Playwright)

Scrapes HackerOne Hacktivity for a given month and aggregates bounty payouts by
program (team). Outputs JSON and CSV files to the Bastet logs directory.

Usage:
  ./scraper.py --month 2025-08

Notes:
- This scraper only aggregates disclosed reports that include public bounty
  amounts. Private/undisclosed bounties will not be counted.
- It paginates through Hacktivity and stops when report dates fall outside the
  requested month.
- It does not require authentication.
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
import typer
from playwright.async_api import Browser, BrowserContext, Page, async_playwright

app = typer.Typer(add_completion=False, rich_markup_mode="markdown")


@dataclass
class ReportEntry:
    report_id: str
    program: str
    bounty_usd: float
    disclosed_at: datetime


HACKTIVITY_BASE = "https://hackerone.com/hacktivity"


def ensure_logs_dirs() -> Tuple[Path, Path]:
    project_root = Path(__file__).resolve().parents[2]
    logs_root = project_root / "logs"
    tool_outputs = logs_root / "tool_outputs"
    tool_outputs.mkdir(parents=True, exist_ok=True)
    findings_dir = logs_root / "findings"
    findings_dir.mkdir(parents=True, exist_ok=True)
    return tool_outputs, findings_dir


def parse_month(month: str) -> Tuple[datetime, datetime]:
    start = datetime.strptime(month, "%Y-%m").replace(tzinfo=timezone.utc)
    # compute end as first day next month
    year = start.year + (1 if start.month == 12 else 0)
    next_month = 1 if start.month == 12 else start.month + 1
    end = datetime(year, next_month, 1, tzinfo=timezone.utc)
    return start, end


def parse_currency_to_float(text: str) -> Optional[float]:
    # Examples: "$1,000", "US$2,345.67"
    m = re.findall(r"[0-9][0-9,]*\.?[0-9]*", text.replace("\xa0", " "))
    if not m:
        return None
    try:
        return float(m[0].replace(",", ""))
    except Exception:
        return None


async def open_context(
    headless: bool = True,
    slow_mo_ms: int = 0,
    default_timeout_ms: int = 45000,
) -> Tuple[Browser, BrowserContext, Page]:
    pw = await async_playwright().start()
    browser = await pw.chromium.launch(headless=headless, slow_mo=slow_mo_ms or 0)
    context = await browser.new_context()
    context.set_default_timeout(default_timeout_ms)
    page = await context.new_page()
    return browser, context, page


async def close_context(browser: Browser, context: BrowserContext) -> None:
    await context.close()
    await browser.close()


async def load_hacktivity_page(
    page: Page,
    page_num: int,
    month: Optional[str],
    page_wait_ms: int,
) -> None:
    # Use pagination with a precise querystring to focus results.
    # Querystring syntax: type:report bounty:>0 disclosed:YYYY-MM
    q = "type:report bounty:>0"
    if month:
        q += f" disclosed:{month}"
    from urllib.parse import quote
    querystring = quote(q, safe="")
    url = (
        f"{HACKTIVITY_BASE}?page={page_num}"
        f"&order_by=latest_disclosable_activity_at&querystring={querystring}"
    )
    await page.goto(url, wait_until="domcontentloaded")
    try:
        # Wait for either report links to appear or an empty-state message
        await page.wait_for_selector('a[href^="/reports/"]', timeout=page_wait_ms)
    except Exception:
        # Fallback: give the app more time to hydrate
        await page.wait_for_timeout(page_wait_ms)


async def extract_reports_on_page(page: Page) -> List[Tuple[str, str]]:
    # Attempt to select report cards. HackerOne may change markup; keep selectors resilient.
    # Return list of (report_id, href)
    entries: List[Tuple[str, str]] = []
    # Each report is usually an <a> link to /reports/<id> with surrounding card.
    report_links = await page.query_selector_all('a[href^="/reports/"]')
    seen_ids = set()
    for link in report_links:
        href = await link.get_attribute("href")
        if not href:
            continue
        m = re.search(r"/reports/(\d+)", href)
        if not m:
            continue
        report_id = m.group(1)
        if report_id in seen_ids:
            continue
        seen_ids.add(report_id)
        entries.append((report_id, href))
    return entries


async def extract_details_from_report(
    context: BrowserContext,
    href: str,
    report_wait_ms: int,
) -> Optional[ReportEntry]:
    url = href
    if href.startswith("/"):
        url = "https://hackerone.com" + href
    page = await context.new_page()
    try:
        await page.goto(url, wait_until="domcontentloaded")
        try:
            await page.wait_for_selector("time", timeout=report_wait_ms)
        except Exception:
            await page.wait_for_timeout(report_wait_ms)
        # Program name: look for breadcrumb or header link to team
        program = ""
        # Try a few selectors
        sel_candidates = [
            'a[href^="/"][data-test*="profile" i]',
            'a[href^="/"]:has(img)',
            'header a[href^="/"]',
            'a[href^="/"][class*="team" i]'
        ]
        for sel in sel_candidates:
            el = await page.query_selector(sel)
            if el:
                t = (await el.inner_text()) or ""
                t = t.strip()
                if t and len(t) > 1:
                    program = t
                    break
        if not program:
            # fallback from document title
            title = await page.title()
            m = re.search(r"to\s+([^|\-]+)", title or "")
            if m:
                program = m.group(1).strip()
        if not program:
            program = "Unknown Program"

        # Bounty amount: search for text containing 'bounty' and currency
        text = await page.inner_text("body")
        bounty_usd = 0.0
        mb = re.search(r"bounty[^\n\r$]*\$([0-9][0-9,]*\.?[0-9]*)", text, re.IGNORECASE)
        if mb:
            try:
                bounty_usd = float(mb.group(1).replace(",", ""))
            except Exception:
                bounty_usd = 0.0

        # Disclosed date from time tag
        disclosed_at = None
        time_node = await page.query_selector("time")
        if time_node:
            dt_val = await (await time_node.get_property("dateTime")).json_value()
            if dt_val:
                try:
                    disclosed_at = datetime.fromisoformat(str(dt_val).replace("Z", "+00:00"))
                except Exception:
                    disclosed_at = None
        if not disclosed_at:
            mdate = re.search(r"(\d{4}-\d{2}-\d{2})", text)
            if mdate:
                disclosed_at = datetime.strptime(mdate.group(1), "%Y-%m-%d").replace(tzinfo=timezone.utc)
        if not disclosed_at:
            return None

        m = re.search(r"/reports/(\d+)", url)
        report_id = m.group(1) if m else url

        return ReportEntry(
            report_id=report_id,
            program=program,
            bounty_usd=bounty_usd,
            disclosed_at=disclosed_at,
        )
    finally:
        await page.close()


async def scrape_month(
    month: str,
    max_pages: int = 30,
    headless: bool = True,
    slow_mo_ms: int = 0,
    page_wait_ms: int = 4000,
    report_wait_ms: int = 2500,
    nav_timeout_ms: int = 45000,
) -> List[ReportEntry]:
    start, end = parse_month(month)
    browser, context, page = await open_context(
        headless=headless, slow_mo_ms=slow_mo_ms, default_timeout_ms=nav_timeout_ms
    )
    try:
        all_entries: List[ReportEntry] = []
        for p in range(1, max_pages + 1):
            await load_hacktivity_page(page, p, month, page_wait_ms)
            link_entries = await extract_reports_on_page(page)
            if not link_entries:
                break
            # visit each report for reliable details
            for (_id, href) in link_entries:
                details = await extract_details_from_report(context, href, report_wait_ms)
                if not details:
                    continue
                if start <= details.disclosed_at < end:
                    all_entries.append(details)
                elif details.disclosed_at < start:
                    # we've paged beyond the month
                    break
            # If entries on this page are all after end (too new), continue pagination
        return all_entries
    finally:
        await close_context(browser, context)


def aggregate_by_program(entries: List[ReportEntry]) -> pd.DataFrame:
    rows = [
        {
            "program": e.program,
            "bounty_usd": float(e.bounty_usd or 0.0),
            "report_id": e.report_id,
            "disclosed_at": e.disclosed_at.isoformat(),
        }
        for e in entries
        if e.bounty_usd and e.program
    ]
    if not rows:
        return pd.DataFrame(columns=["program", "total_bounty_usd", "report_count"])
    df = pd.DataFrame(rows)
    agg = (
        df.groupby("program")
        .agg(total_bounty_usd=("bounty_usd", "sum"), report_count=("report_id", "count"))
        .reset_index()
        .sort_values(["total_bounty_usd", "report_count"], ascending=[False, False])
    )
    return agg


def save_outputs(month: str, entries: List[ReportEntry], agg: pd.DataFrame) -> Tuple[Path, Path]:
    tool_outputs, findings_dir = ensure_logs_dirs()
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    base = f"hackerone_payouts_{month}_{ts}"

    # Raw entries JSON
    raw_path = tool_outputs / f"{base}_raw.json"
    with raw_path.open("w", encoding="utf-8") as f:
        json.dump(
            [
                {
                    "report_id": e.report_id,
                    "program": e.program,
                    "bounty_usd": e.bounty_usd,
                    "disclosed_at": e.disclosed_at.isoformat(),
                }
                for e in entries
            ],
            f,
            indent=2,
        )

    # Aggregated CSV
    agg_path = findings_dir / f"{base}_agg.csv"
    agg.to_csv(agg_path, index=False)

    return raw_path, agg_path


@app.command()
def main(
    month: str = typer.Option(..., help="Target month in YYYY-MM format, e.g. 2025-08"),
    top: int = typer.Option(10, help="Number of top programs to display"),
    max_pages: int = typer.Option(30, help="Max Hacktivity pages to scan"),
    headless: bool = typer.Option(
        False,
        "--headless/--no-headless",
        help="Run browser in headless mode",
    ),
    slow_mo: int = typer.Option(0, help="Slow down actions by N milliseconds"),
    page_wait_ms: int = typer.Option(6000, help="Wait time after navigating a results page"),
    report_wait_ms: int = typer.Option(4000, help="Wait time after opening a report page"),
    nav_timeout_ms: int = typer.Option(60000, help="Default navigation timeout"),
):
    """Scrape HackerOne Hacktivity and output top programs by total bounty for the month."""

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    async def _run():
        entries = await scrape_month(
            month,
            max_pages=max_pages,
            headless=headless,
            slow_mo_ms=slow_mo,
            page_wait_ms=page_wait_ms,
            report_wait_ms=report_wait_ms,
            nav_timeout_ms=nav_timeout_ms,
        )
        agg = aggregate_by_program(entries)
        raw_path, agg_path = save_outputs(month, entries, agg)

        typer.echo(f"Saved raw entries to: {raw_path}")
        typer.echo(f"Saved aggregation to: {agg_path}")

        if not agg.empty:
            typer.echo("\nTop programs:")
            display = agg.head(top)
            # Pretty print
            for i, row in enumerate(display.itertuples(index=False), start=1):
                typer.echo(
                    f"{i:>2}. {row.program}  |  ${row.total_bounty_usd:,.2f}  |  reports: {row.report_count}"
                )
        else:
            typer.echo("No bounty data found for the requested month.")

    asyncio.run(_run())


if __name__ == "__main__":
    app()


