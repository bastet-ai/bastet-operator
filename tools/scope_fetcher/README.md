# Scope Fetcher

Automated program policy and scope documentation tool using Playwright for dynamic content extraction.

## Purpose

Fetches and snapshots program policies and scope information from HackerOne program pages, handling dynamic content loading and providing dated documentation for the targets wiki.

## Features

- **Dynamic Content Handling**: Uses Playwright to wait for page hydration and dynamic loading
- **Retry Logic**: Configurable retries with wait times for reliable content extraction
- **Content Validation**: Minimum character thresholds to ensure meaningful content capture
- **URL Integration**: Includes program policy URLs in output for reference
- **Scope Documentation**: Updates target scope files with timestamped snapshots

## Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install playwright typer
playwright install
```

## Usage

```bash
# Activate environment
source venv/bin/activate

# Fetch scope for specific programs
python fetch_scopes.py --programs uber tiktok gitlab

# With debugging options
python fetch_scopes.py --programs uber --no-headless --slow-mo 1000 --retries 3

# Batch processing
python fetch_scopes.py --programs $(cat ../targets/docs/programs/high-value-list.txt)
```

## Command Options

- `--programs`: Space-separated list of program handles to fetch
- `--no-headless`: Run browser visibly for debugging
- `--slow-mo`: Milliseconds to slow down operations (default: 250)
- `--wait-ms`: Wait time between retries in milliseconds (default: 2000)
- `--retries`: Number of retry attempts for failed fetches (default: 2)
- `--min-chars`: Minimum character count for valid content (default: 500)

## Output

Updates scope files in the targets wiki:
- `../targets/docs/programs/{program}/scope.md`
- Includes snapshot date, program policy URL, and captured scope text
- Maintains previous content if fetch fails

## Integration with Bastet Ecosystem

- **Input**: Program handles from targets wiki
- **Output**: Updated scope documentation in targets repository
- **Logging**: Detailed execution logs to `../../logs/tool_outputs/`
- **Error Handling**: Graceful failure with preserved existing content

## Technical Implementation

- **Browser Engine**: Chromium via Playwright
- **Content Extraction**: CSS selectors targeting policy sections
- **Dynamic Loading**: Explicit waits and scroll triggers for hydration
- **Retry Strategy**: Progressive backoff with content validation
- **File Safety**: Atomic file updates to prevent corruption

## Debugging

For content extraction issues:
1. Use `--no-headless` to observe browser behavior
2. Increase `--slow-mo` to see step-by-step execution
3. Add `--retries` for unstable page loading
4. Check minimum character threshold with `--min-chars`

## Scope Compliance

- **Respectful**: Uses appropriate delays and respects robots.txt
- **Authorized**: Only accesses publicly available program information
- **Rate Limited**: Built-in delays prevent server overload
- **Ethical**: Designed for legitimate security research documentation

---

🐱 *"Knowledge of the hunting grounds changes with the seasons. Keep the maps current, the boundaries clear."* - Bastet
