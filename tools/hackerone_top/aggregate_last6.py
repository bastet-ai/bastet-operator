#!/usr/bin/env python3
from __future__ import annotations

import os
from datetime import datetime
from typing import List, Tuple

import pandas as pd
import typer

from api_client import fetch_hacktivity, fetch_hacktivity_unfiltered, aggregate_by_program

app = typer.Typer(add_completion=False)


def month_iter(end_month: str, n: int) -> List[str]:
    # end_month inclusive, format YYYY-MM
    y, m = map(int, end_month.split("-"))
    months: List[str] = []
    for i in range(n):
        yy = y
        mm = m - i
        while mm <= 0:
            mm += 12
            yy -= 1
        months.append(f"{yy:04d}-{mm:02d}")
    return list(reversed(months))


@app.command()
def main(
    end_month: str = typer.Option(..., help="End month inclusive, YYYY-MM (e.g., 2025-08)"),
    months: int = typer.Option(6, help="Number of months to aggregate (inclusive of end_month)"),
    per_page: int = typer.Option(100, help="API page size"),
    max_pages: int = typer.Option(100, help="Max pages per month"),
    username: str = typer.Option(..., envvar="H1_USERNAME"),
    token: str = typer.Option(..., envvar="H1_API_TOKEN"),
    top: int = typer.Option(10, help="Top N programs to display"),
):
    months_list = month_iter(end_month, months)
    all_rows: List[dict] = []

    for month in months_list:
        items = fetch_hacktivity(month, username, token, per_page=per_page, max_pages=max_pages)
        if not items:
            items = fetch_hacktivity_unfiltered(month, username, token, per_page=per_page, max_pages=max_pages)
        for it in items:
            all_rows.append({
                "month": month,
                "program": it.program,
                "bounty_usd": float(it.total_awarded_amount or 0.0),
                "report_id": it.id,
                "activity_at": it.disclosed_at.isoformat(),
            })

    if not all_rows:
        typer.echo("No data for the requested window.")
        raise typer.Exit(code=0)

    df = pd.DataFrame(all_rows)
    agg = (
        df.groupby("program")
        .agg(total_bounty_usd=("bounty_usd", "sum"), report_count=("report_id", "count"))
        .reset_index()
        .sort_values(["total_bounty_usd", "report_count"], ascending=[False, False])
    )

    typer.echo(f"Aggregated window: {months_list[0]} to {months_list[-1]}")
    for i, row in enumerate(agg.head(top).itertuples(index=False), start=1):
        typer.echo(f"{i:>2}. {row.program}  |  ${row.total_bounty_usd:,.2f}  |  reports: {row.report_count}")


if __name__ == "__main__":
    app()


