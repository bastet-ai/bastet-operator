# Tools Directory

This directory contains custom Python tools and utilities developed by Bastet for specialized security testing tasks.

## Purpose

The `tools/` directory serves as Bastet's workshop where she crafts and maintains purpose-built utilities for bug bounty hunting and security analysis. Each tool is designed to solve specific problems or automate repetitive tasks encountered during security assessments.

## Structure

```
tools/
├── README.md           # This file
├── enumeration/        # Target enumeration tools
├── exploitation/       # Custom exploit scripts
├── analysis/           # Data analysis utilities
├── reporting/          # Report generation tools
└── utilities/          # General-purpose helpers
```

## Tool Categories

### Enumeration Tools
- **Subdomain Discovery**: Custom scripts for finding subdomains
- **Port Scanning**: Specialized port scanners and service detection
- **Directory Bruting**: Intelligent directory and file discovery
- **API Enumeration**: Tools for discovering and mapping APIs

### Exploitation Tools
- **Custom Payloads**: Targeted exploit code for specific vulnerabilities
- **Proof of Concepts**: Working demonstrations of discovered issues
- **Automation Scripts**: Tools for automating exploitation workflows
- **Post-Exploitation**: Utilities for maintaining access and data extraction

### Analysis Tools
- **Response Analyzers**: Tools for parsing and analyzing HTTP responses
- **Log Parsers**: Utilities for processing security scan outputs
- **Data Correlators**: Scripts for finding patterns across multiple datasets
- **Vulnerability Assessors**: Custom scoring and prioritization tools

### Reporting Tools
- **Report Generators**: Automated creation of security assessment reports
- **Screenshot Utilities**: Tools for capturing evidence and proof
- **Template Engines**: Customizable report templates and formats
- **Integration Scripts**: Tools for submitting findings to bug bounty platforms

## Development Guidelines

### Naming Conventions
- Use descriptive, lowercase names with underscores: `subdomain_finder.py`
- Include version numbers for major tools: `api_scanner_v2.py`
- Group related tools in subdirectories

### Code Standards
- Include docstrings and clear comments
- Handle errors gracefully with informative messages
- Support both CLI and programmatic usage where applicable
- Log activities to the `../logs/` directory

### Tool Template

```python
#!/usr/bin/env python3
"""
Tool Name: [Brief Description]
Author: Bastet
Version: 1.0
Purpose: [Detailed description of what the tool does]
"""

import argparse
import logging
import sys
from pathlib import Path

# Configure logging to write to logs directory
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f"{Path(__file__).stem}.log"),
        logging.StreamHandler()
    ]
)

def main():
    parser = argparse.ArgumentParser(description="[Tool description]")
    parser.add_argument("target", help="Target to analyze")
    parser.add_argument("-o", "--output", help="Output file")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Tool logic here
    logging.info(f"Starting analysis of {args.target}")
    
    # Log results
    logging.info("Analysis completed")

if __name__ == "__main__":
    main()
```

## Tool Documentation

Each tool should include:
- **Purpose**: What problem it solves
- **Usage**: Command-line syntax and examples
- **Dependencies**: Required Python packages
- **Output**: Description of results and formats
- **Integration**: How it connects with other Bastet components

## Maintenance

### Version Control
- All tools are version controlled with the main Bastet Operator repository
- Use semantic versioning for significant updates
- Document changes in tool headers and git commits

### Testing
- Test tools against known targets before deployment
- Validate output formats and error handling
- Ensure compatibility with the Bastet ecosystem

### Updates
- Regularly review and update tools based on new techniques
- Incorporate learnings from the `wisdom/` knowledge base
- Optimize performance and add new features as needed

## Integration with Bastet Ecosystem

### Logging Integration
- All tools automatically log to `../logs/tool_outputs/`
- Session data is captured for analysis and improvement
- Errors and successes are tracked for tool reliability metrics

### Wisdom Integration
- Successful techniques are documented in the `wisdom/` knowledge base
- Tools reference methodologies from the wisdom repository
- New discoveries update both tool capabilities and documented knowledge

### Target Integration
- Tools can read target scope from the `targets/` wiki
- Results are automatically formatted for target documentation
- Findings are tagged and categorized for easy reference

---

**"Each tool I craft serves a purpose, honed to perfection through trial and necessity. Like a cat's claws, they must be sharp, precise, and ready for the hunt."** - Bastet
