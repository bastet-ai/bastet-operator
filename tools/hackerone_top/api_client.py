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
    # total_awarded_amount present and > 0
    return f"disclosed_at:[{s} TO {e}) total_awarded_amount:>0"


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
    cursor: Optional[str] = None

    for _ in range(max_pages):
        params = {
            "querystring": q,
            "page[size]": per_page,
        }
        if cursor:
            params["page[cursor]"] = cursor
        resp = requests.get(API_URL, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        # Extract items
        for node in data.get("data", []):
            attrs = node.get("attributes", {})
            relationships = node.get("relationships", {})
            team = relationships.get("team", {}).get("data", {})
            program = team.get("attributes", {}).get("name") if team else None
            if not program:
                # Some responses include team details in included
                included_by_id = {inc.get("id"): inc for inc in data.get("included", [])}
                if team and team.get("id") in included_by_id:
                    inc = included_by_id[team.get("id")]
                    program = inc.get("attributes", {}).get("name")

            total_awarded = attrs.get("total_awarded_amount") or 0
            disclosed_at = attrs.get("disclosed_at")
            if not disclosed_at:
                continue
            dt = datetime.fromisoformat(str(disclosed_at).replace("Z", "+00:00"))

            items.append(
                HacktivityItem(
                    id=node.get("id", ""),
                    program=program or "Unknown Program",
                    total_awarded_amount=float(total_awarded or 0.0),
                    disclosed_at=dt,
                )
            )

        # Pagination
        cursor = data.get("links", {}).get("next", {}).get("href")
        if not cursor:
            break
        # Cursor may be a full URL; extract page[cursor] if present
        if "page[cursor]=" in cursor:
            cursor = cursor.split("page[cursor]=", 1)[1]

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


