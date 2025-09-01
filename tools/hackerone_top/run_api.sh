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
pip install requests pandas typer >/dev/null

MONTH="${1:-2025-08}"

if [ -z "${H1_USERNAME:-}" ] || [ -z "${H1_API_TOKEN:-}" ]; then
  echo "Missing H1_USERNAME or H1_API_TOKEN in environment" >&2
  exit 1
fi

python "$TOOL_DIR/api_client.py" --month "$MONTH" --top 10


