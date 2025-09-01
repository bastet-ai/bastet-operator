#!/usr/bin/env python3
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import List

import typer
from playwright.async_api import async_playwright

app = typer.Typer(add_completion=False)


PROGRAMS = [
    ("uber", "Uber"),
    ("eternal", "Eternal"),
    ("okg", "OKG"),
    ("tiktok", "TikTok"),
    ("sheer_bbp", "Sheer"),
    ("gitlab", "GitLab"),
    ("paypal", "PayPal"),
    ("ferrero", "Ferrero"),
    ("mediatek", "MediaTek"),
    ("zooplus", "Zooplus"),
]


async def fetch_policy_text(handle: str, headless: bool, slow_mo_ms: int, wait_ms: int, retries: int, min_chars: int) -> str:
    url = f"https://hackerone.com/{handle}"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless, slow_mo=slow_mo_ms or 0)
        context = await browser.new_context()
        page = await context.new_page()

        attempt = 0
        best_text = ""
        while attempt < retries:
            attempt += 1
            await page.goto(url, wait_until="domcontentloaded")
            try:
                await page.wait_for_selector("main", timeout=wait_ms)
            except Exception:
                await page.wait_for_timeout(wait_ms)
            # Nudge hydration
            try:
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(500)
                await page.evaluate("window.scrollTo(0, 0)")
            except Exception:
                pass

            text = ""
            candidate_selectors = [
                "section:has(h2:has-text('Scope'))",
                "section:has(h2:has-text('Program Rules'))",
                "section:has(h2:has-text('Policy'))",
                "section[aria-label*='Scope' i]",
                "div:has(h2:has-text('Scope'))",
                "div:has(h2:has-text('Policy'))",
            ]
            for sel in candidate_selectors:
                try:
                    el = await page.query_selector(sel)
                    if el:
                        t = await el.inner_text()
                        if t and len(t.strip()) > len(text):
                            text = t.strip()
                except Exception:
                    continue
            if not text:
                try:
                    main = await page.query_selector("main")
                    if main:
                        t = await main.inner_text()
                        if t and t.strip():
                            text = t.strip()
                except Exception:
                    pass

            if len(text) >= min_chars:
                best_text = text
                break
            if len(text) > len(best_text):
                best_text = text
            # Backoff and try again
            await page.wait_for_timeout(wait_ms)

        await context.close()
        await browser.close()
        return best_text


def update_scope_file(project_root: Path, program_dir: str, program_name: str, policy_text: str, program_url: str) -> None:
    path = project_root / "targets" / "docs" / "programs" / program_dir / "scope.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    snapshot_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = []
    lines.append(f"# Scope - {program_name}")
    lines.append("")
    lines.append(f"**Snapshot Date**: {snapshot_date}")
    lines.append("")
    lines.append(f"**Program Policy URL**: {program_url}")
    lines.append("")
    lines.append("## Official Policy / Scope")
    lines.append("")
    if policy_text:
        # Keep it simple; not quoting all lines to avoid huge blocks
        lines.append(policy_text)
    else:
        lines.append("[Policy text could not be captured automatically]")
    lines.append("")
    lines.append("## Parsed Scope (to fill)")
    lines.append("")
    lines.append("### In Scope")
    lines.append("-")
    lines.append("")
    lines.append("### Out of Scope")
    lines.append("-")
    lines.append("")
    lines.append("### Changes")
    lines.append(f"- {snapshot_date}: Snapshot recorded.")
    path.write_text("\n".join(lines), encoding="utf-8")


@app.command()
def main(
    programs: List[str] = typer.Option([p for p, _ in PROGRAMS], help="Program handles to fetch"),
    no_headless: bool = typer.Option(False, "--no-headless", help="Run non-headless for debugging"),
    slow_mo: int = typer.Option(0, help="Slow down actions in ms"),
    wait_ms: int = typer.Option(6000, help="Wait time for page hydration in ms"),
    retries: int = typer.Option(4, help="Number of retry attempts per program"),
    min_chars: int = typer.Option(800, help="Minimum characters to accept as valid policy text"),
):
    project_root = Path(__file__).resolve().parents[2]

    async def run_all():
        for handle, name in PROGRAMS:
            if handle not in programs:
                continue
            text = await fetch_policy_text(handle, headless=not no_headless, slow_mo_ms=slow_mo, wait_ms=wait_ms, retries=retries, min_chars=min_chars)
            dir_name = handle if handle != "sheer_bbp" else "sheer"
            update_scope_file(project_root, dir_name, name, text, f"https://hackerone.com/{handle}")

    asyncio.run(run_all())


if __name__ == "__main__":
    app()


