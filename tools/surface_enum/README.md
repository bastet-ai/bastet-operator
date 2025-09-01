# Surface Enumeration Framework

Comprehensive attack surface enumeration tool for systematic reconnaissance of bug bounty targets.

## Purpose

Performs systematic attack surface discovery through subdomain enumeration, web service probing, and interesting endpoint identification. Designed for ethical security research and bug bounty reconnaissance.

## Features

- **Multi-Method Subdomain Discovery**: Manual patterns + external tool integration
- **Web Service Enumeration**: HTTP/HTTPS probing with service metadata
- **Endpoint Discovery**: Automated testing of common sensitive paths
- **Comprehensive Logging**: Structured output for analysis and reporting
- **Fallback Mechanisms**: Graceful degradation when external tools unavailable
- **Professional Output**: Clean summaries with actionable intelligence

## Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install typer
```

## Usage

```bash
# Activate environment
source venv/bin/activate

# Basic enumeration
python enumerate.py target.com

# Skip specific phases
python enumerate.py target.com --skip-subs --skip-web --skip-paths

# Full enumeration (slower but comprehensive)
python enumerate.py target.com --full
```

## Command Options

- `target`: Primary domain to enumerate (required)
- `--full`: Run comprehensive enumeration with extended wordlists
- `--skip-subs`: Skip subdomain discovery phase
- `--skip-web`: Skip web service probing phase  
- `--skip-paths`: Skip interesting endpoint discovery phase

## Enumeration Phases

### Phase 1: Subdomain Discovery
- **External Tools**: subfinder, assetfinder (if available)
- **Manual Discovery**: Common subdomain pattern testing
- **DNS Validation**: Direct nslookup verification
- **Output**: Complete subdomain list with validation status

### Phase 2: Web Service Discovery  
- **HTTP Probing**: Both HTTP and HTTPS testing
- **Service Metadata**: Headers, redirects, technologies
- **Fallback Methods**: Curl-based probing when httpx unavailable
- **Output**: Live service inventory with technical details

### Phase 3: Endpoint Discovery
- **Sensitive Paths**: Security, configuration, admin endpoints
- **API Discovery**: REST, GraphQL, documentation endpoints
- **Information Disclosure**: Debug, status, version endpoints
- **Output**: Accessible endpoints with response analysis

## Tested Endpoints

### Security & Policy
- `/.well-known/security.txt` - Security contact information
- `/robots.txt` - Search engine directives and path disclosure
- `/sitemap.xml` - Site structure enumeration

### Administrative Interfaces
- `/admin` - Administrative dashboards
- `/config` - Configuration interfaces
- `/debug` - Debug panels and diagnostics

### API Infrastructure
- `/api` - API gateways and endpoints
- `/graphql` - GraphQL query interfaces
- `/swagger` - API documentation
- `/docs` - Developer documentation

### System Information
- `/health` - Health check endpoints
- `/status` - System status interfaces
- `/version` - Version information disclosure
- `/.env` - Environment variable files

## Output Structure

```
logs/surface_enum/target.com/
├── target.com_complete_enumeration.json    # Full results
├── target.com_all_subdomains.txt          # Discovered subdomains
├── target.com_web_services.json           # Live web services
├── target.com_interesting_endpoints.json   # Accessible endpoints
└── target.com_manual_subs.txt             # Manual discovery results
```

## Integration with External Tools

### Supported Tools (optional)
- **subfinder**: Enhanced subdomain discovery
- **assetfinder**: Additional subdomain sources
- **httpx**: Advanced web service probing

### Installation of External Tools
```bash
# Go-based tools
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/tomnomnom/assetfinder@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
```

## Security & Ethics

### Scope Compliance
- **Authorized Testing Only**: Verify target authorization before enumeration
- **Respectful Reconnaissance**: Built-in delays and rate limiting
- **Scope Awareness**: Check program scope before running
- **Professional Approach**: Minimal noise, maximum intelligence

### Rate Limiting
- **Built-in Delays**: Prevents server overload
- **Timeout Controls**: Prevents hanging requests
- **Retry Logic**: Handles temporary failures gracefully
- **Resource Limits**: Memory and time constraints

## Technical Implementation

### Architecture
- **Modular Design**: Separate phases can be run independently
- **Fallback Systems**: Graceful degradation without external tools
- **Error Handling**: Comprehensive exception management
- **Logging Framework**: Structured output for analysis

### Performance
- **Concurrent Processing**: Parallel subdomain validation
- **Efficient Probing**: Smart timeout and retry strategies
- **Memory Management**: Stream processing for large result sets
- **Cache-Friendly**: Respects HTTP caching headers

## Troubleshooting

### Common Issues
- **External Tool Missing**: Framework continues with manual methods
- **DNS Resolution Fails**: Check network connectivity and DNS settings
- **Timeout Errors**: Increase timeout values or check target responsiveness
- **Permission Denied**: Verify file system permissions for log directory

### Debug Mode
```bash
# Verbose output
python enumerate.py target.com --verbose

# Single-threaded for debugging
python enumerate.py target.com --threads 1

# Extended timeouts
python enumerate.py target.com --timeout 30
```

## Integration with Bastet Ecosystem

- **Target Input**: Domain lists from `../targets/` wiki
- **Output Logging**: Results stored in `../../logs/surface_enum/`
- **Intelligence Updates**: Findings integrated into target documentation
- **Methodology Sharing**: Successful techniques documented in `../wisdom/`

---

🐱 *"The hunter maps the terrain before the hunt. Every subdomain, every service, every path - knowledge is the foundation of successful pursuit."* - Bastet
