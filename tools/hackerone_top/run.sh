#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TOOL_DIR="$ROOT_DIR/tools/hackerone_top"
VENV_DIR="$TOOL_DIR/venv"

if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"
pip install --upgrade pip >/dev/null
pip install playwright pandas pydantic typer rich >/dev/null
python -m playwright install --with-deps chromium >/dev/null || true

MONTH="${1:-2025-08}"
TOP="${2:-10}"

python "$TOOL_DIR/scraper.py" --month "$MONTH" --top "$TOP"


