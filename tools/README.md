# Tools Directory

This directory contains custom Python tools developed by Bastet for bug bounty reconnaissance and analysis.

## Tools Overview

### 🔍 **hackerone_top/**
HackerOne Hacktivity analysis and top programs identification
- **Purpose**: Aggregate bounty payout data from HackerOne API
- **Key Scripts**: `api_client.py`, `aggregate_last6.py`
- **Usage**: Identify high-value targets by payout analysis

### 🌐 **surface_enum/**
Attack surface enumeration framework
- **Purpose**: Systematic subdomain discovery and endpoint enumeration
- **Key Scripts**: `enumerate.py`
- **Usage**: Map target attack surfaces for security assessment

### 📄 **scope_fetcher/**
Program scope and policy documentation
- **Purpose**: Automated capture of program policies from HackerOne
- **Key Scripts**: `fetch_scopes.py`
- **Usage**: Maintain up-to-date scope documentation

## Development Guidelines

### Virtual Environments
Each tool maintains its own virtual environment to isolate dependencies:
```bash
cd <tool_directory>
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Tool Standards
- **Language**: Python 3.8+
- **CLI Framework**: Typer for command-line interfaces
- **Output**: Structured JSON and CSV formats
- **Logging**: Comprehensive output logging to `../../logs/`
- **Error Handling**: Graceful failure with informative messages

### Integration with Bastet Ecosystem
- **Input**: Target lists from `../targets/` wiki
- **Output**: Findings logged to `../logs/` directory
- **Documentation**: Process updates to `../wisdom/` wiki
- **Coordination**: Session summaries stored in `../logs/sessions/`

## Output Management

All tool outputs are stored in the `../logs/` directory:
- **Raw Data**: `logs/tool_outputs/` - Unprocessed tool output
- **Findings**: `logs/findings/` - Analyzed and filtered results
- **Sessions**: `logs/sessions/` - Session summaries and interaction logs

## Security Considerations

- **API Keys**: Stored in `.env` files (gitignored)
- **Rate Limiting**: Respectful of target rate limits
- **Scope Compliance**: Tools validate against program scope
- **Ethical Usage**: All tools designed for authorized testing only

---

🐱 *"Every tool is an extension of the hunter's senses. Craft them with precision, wield them with wisdom."* - Bastet