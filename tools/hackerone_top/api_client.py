#!/usr/bin/env python3
"""
HackerOne Hacktivity API Aggregator

Uses the official HackerOne Hacker API v1 to fetch hacktivity items and
aggregate total_awarded_amount by program for a given month.

Auth: HTTP Basic with username and API token.
Env vars:
  H1_USERNAME
  H1_API_TOKEN

Endpoint:
  GET https://api.hackerone.com/v1/hackers/hacktivity

Filters (Lucene-style) examples:
  disclosed_at:[2025-08-01 TO 2025-09-01) total_awarded_amount:>0

"""
from __future__ import annotations

import base64
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
import requests
import typer

app = typer.Typer(add_completion=False, rich_markup_mode="markdown")


API_URL = "https://api.hackerone.com/v1/hackers/hacktivity"


@dataclass
class HacktivityItem:
    id: str
    program: str
    total_awarded_amount: float
    disclosed_at: datetime


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
    year = start.year + (1 if start.month == 12 else 0)
    next_month = 1 if start.month == 12 else start.month + 1
    end = datetime(year, next_month, 1, tzinfo=timezone.utc)
    return start, end


def build_filter(month: str) -> str:
    start, end = parse_month(month)
    # ISO dates without timezone in filter; API interprets UTC
    s = start.strftime("%Y-%m-%d")
    e = end.strftime("%Y-%m-%d")
    # Focus on bounty awards that happened within the month
    # and ensure an amount is present
    return (
        f"latest_disclosable_action:Activities::BountyAwarded "
        f"latest_disclosable_activity_at:[{s} TO {e}) "
        f"total_awarded_amount:>0"
    )


def get_auth_header(username: str, token: str) -> Dict[str, str]:
    auth_str = f"{username}:{token}".encode()
    return {"Authorization": f"Basic {base64.b64encode(auth_str).decode()}"}


def fetch_hacktivity(month: str, username: str, token: str, per_page: int = 100, max_pages: int = 100) -> List[HacktivityItem]:
    headers = {
        **get_auth_header(username, token),
        "Accept": "application/json",
        "User-Agent": "Bastet-Operator/1.0",
    }
    q = build_filter(month)
    items: List[HacktivityItem] = []
    next_url: Optional[str] = None

    def build_param_variants(query: str, cursor_token: Optional[str]) -> List[Dict[str, str]]:
        base = {
            "page[size]": str(per_page),
            "include": "program,award",
            "fields[program]": "name,handle",
        }
        if cursor_token:
            base["page[cursor]"] = cursor_token
        variants = []
        for key in ("querystring", "filter[query]", "query", "filter[q]"):
            p = dict(base)
            p[key] = query
            variants.append(p)
        return variants

    for page_index in range(max_pages):
        # Build request
        if next_url:
            resp = requests.get(next_url, headers=headers, timeout=30)
        else:
            params_list = build_param_variants(q, None)
            # try param variants until one returns data or 200
            last_exc = None
            resp = None
            for params in params_list:
                try:
                    resp = requests.get(API_URL, headers=headers, params=params, timeout=30)
                    if resp.status_code == 200:
                        break
                except Exception as e:  # noqa: BLE001
                    last_exc = e
            if resp is None:
                if last_exc:
                    raise last_exc
                raise RuntimeError("Failed to fetch hacktivity")
        resp.raise_for_status()
        data = resp.json()
        # Save first page debug for troubleshooting
        if page_index == 0:
            tool_outputs, _ = ensure_logs_dirs()
            debug_path = tool_outputs / f"h1_api_debug_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
            try:
                with debug_path.open("w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
            except Exception:
                pass
        # Extract items
        for node in data.get("data", []):
            attrs = node.get("attributes", {})
            relationships = node.get("relationships", {})
            program = None
            included_by_id = {inc.get("id"): inc for inc in data.get("included", [])}
            # Prefer inline program attributes when present
            inline_prog = relationships.get("program", {}).get("data", {})
            if inline_prog:
                program = inline_prog.get("attributes", {}).get("name") or inline_prog.get("attributes", {}).get("handle")
            if not program:
                prog_link = relationships.get("program", {}).get("data")
                if prog_link and prog_link.get("id") in included_by_id:
                    inc = included_by_id.get(prog_link.get("id"))
                    if inc:
                        program = inc.get("attributes", {}).get("name") or inc.get("attributes", {}).get("handle")

            # Award amount field can vary; try multiple keys
            total_awarded = (
                attrs.get("total_awarded_amount")
                or attrs.get("total_awarded_amount_in_usd")
                or attrs.get("awarded_amount")
                or attrs.get("bounty_amount")
            )
            if not total_awarded:
                # Try to resolve via included award object
                award_link = relationships.get("award", {}).get("data")
                if award_link:
                    inc_award = included_by_id.get(award_link.get("id"))
                    if inc_award:
                        aattrs = inc_award.get("attributes", {})
                        total_awarded = (
                            aattrs.get("amount_in_usd")
                            or aattrs.get("amount")
                        )
            total_awarded = float(total_awarded or 0.0)
            # Determine award activity time for month filtering
            lda = attrs.get("latest_disclosable_activity_at")
            if not lda:
                continue
            dt = datetime.fromisoformat(str(lda).replace("Z", "+00:00"))

            items.append(
                HacktivityItem(
                    id=node.get("id", ""),
                    program=program or "Unknown Program",
                    total_awarded_amount=float(total_awarded or 0.0),
                    disclosed_at=dt,
                )
            )

        # Pagination
        next_link = data.get("links", {}).get("next")
        cursor = None
        if isinstance(next_link, str):
            cursor = next_link
        elif isinstance(next_link, dict):
            cursor = next_link.get("href")
        if not cursor:
            break
        # Cursor may be a full URL; extract page[cursor] if present
        if isinstance(cursor, str) and "page[cursor]=" in cursor:
            cursor = cursor.split("page[cursor]=", 1)[1]

    return items


def fetch_hacktivity_unfiltered(month: str, username: str, token: str, per_page: int = 100, max_pages: int = 200) -> List[HacktivityItem]:
    """Fallback: fetch recent hacktivity without server-side filters and filter locally.

    Stops when items are older than month start to avoid excessive paging.
    """
    start, end = parse_month(month)
    headers = {
        **get_auth_header(username, token),
        "Accept": "application/json",
        "User-Agent": "Bastet-Operator/1.0",
    }
    items: List[HacktivityItem] = []
    cursor: Optional[str] = None

    for _ in range(max_pages):
        params = {
            "page[size]": per_page,
            "include": "team",
            "fields[team]": "name",
        }
        if cursor:
            params["page[cursor]"] = cursor
        resp = requests.get(API_URL, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        included_by_id = {inc.get("id"): inc for inc in data.get("included", [])}
        page_items: List[HacktivityItem] = []
        for node in data.get("data", []):
            attrs = node.get("attributes", {})
            relationships = node.get("relationships", {})
            team_link = relationships.get("team", {}).get("data", {})
            program = None
            if team_link:
                inc = included_by_id.get(team_link.get("id"))
                if inc:
                    program = inc.get("attributes", {}).get("name")

            total_awarded = (
                attrs.get("total_awarded_amount")
                or attrs.get("total_awarded_amount_in_usd")
                or attrs.get("awarded_amount")
                or attrs.get("bounty_amount")
                or 0
            )
            disclosed_at = attrs.get("disclosed_at")
            if not disclosed_at:
                continue
            dt = datetime.fromisoformat(str(disclosed_at).replace("Z", "+00:00"))

            item = HacktivityItem(
                id=node.get("id", ""),
                program=program or "Unknown Program",
                total_awarded_amount=float(total_awarded or 0.0),
                disclosed_at=dt,
            )
            page_items.append(item)

        # local filter
        month_items = [it for it in page_items if start <= it.disclosed_at < end and (it.total_awarded_amount or 0) > 0]
        items.extend(month_items)

        # Stop if the last page item is older than month start
        if page_items and all(it.disclosed_at < start for it in page_items):
            break

        # Pagination
        next_link = data.get("links", {}).get("next")
        href = None
        if isinstance(next_link, str):
            href = next_link
        elif isinstance(next_link, dict):
            href = next_link.get("href")
        if not href:
            break
        next_url = href

    return items


def aggregate_by_program(items: List[HacktivityItem]) -> pd.DataFrame:
    if not items:
        return pd.DataFrame(columns=["program", "total_bounty_usd", "report_count"])
    rows = [
        {
            "program": it.program,
            "bounty_usd": float(it.total_awarded_amount or 0.0),
            "report_id": it.id,
            "disclosed_at": it.disclosed_at.isoformat(),
        }
        for it in items
        if (it.total_awarded_amount or 0.0) > 0
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


def save_outputs(month: str, items: List[HacktivityItem], agg: pd.DataFrame) -> Tuple[Path, Path]:
    tool_outputs, findings_dir = ensure_logs_dirs()
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    base = f"h1_api_payouts_{month}_{ts}"

    raw_path = tool_outputs / f"{base}_raw.json"
    with raw_path.open("w", encoding="utf-8") as f:
        json.dump(
            [
                {
                    "id": it.id,
                    "program": it.program,
                    "total_awarded_amount": it.total_awarded_amount,
                    "disclosed_at": it.disclosed_at.isoformat(),
                }
                for it in items
            ],
            f,
            indent=2,
        )

    agg_path = findings_dir / f"{base}_agg.csv"
    agg.to_csv(agg_path, index=False)
    return raw_path, agg_path


@app.command()
def main(
    month: str = typer.Option(..., help="Target month in YYYY-MM format, e.g. 2025-08"),
    top: int = typer.Option(10, help="Number of top programs to display"),
    per_page: int = typer.Option(100, help="Page size for API pagination"),
    max_pages: int = typer.Option(100, help="Maximum number of pages to fetch"),
    username: Optional[str] = typer.Option(None, envvar="H1_USERNAME", help="HackerOne username"),
    token: Optional[str] = typer.Option(None, envvar="H1_API_TOKEN", help="HackerOne API token"),
):
    if not username:
        username = os.getenv("H1_USERNAME")
    if not token:
        token = os.getenv("H1_API_TOKEN")
    if not username or not token:
        raise typer.Exit("Missing credentials: set H1_USERNAME and H1_API_TOKEN env vars.")

    items = fetch_hacktivity(month, username, token, per_page=per_page, max_pages=max_pages)
    if not items:
        # Fallback path if server-side filters returned nothing
        items = fetch_hacktivity_unfiltered(month, username, token, per_page=per_page, max_pages=max_pages)
    agg = aggregate_by_program(items)
    raw_path, agg_path = save_outputs(month, items, agg)
    typer.echo(f"Saved raw items to: {raw_path}")
    typer.echo(f"Saved aggregation to: {agg_path}")

    if not agg.empty:
        typer.echo("\nTop programs:")
        display = agg.head(top)
        for i, row in enumerate(display.itertuples(index=False), start=1):
            typer.echo(
                f"{i:>2}. {row.program}  |  ${row.total_bounty_usd:,.2f}  |  reports: {row.report_count}"
            )
    else:
        typer.echo("No bounty data returned by API for the requested month.")


if __name__ == "__main__":
    app()


