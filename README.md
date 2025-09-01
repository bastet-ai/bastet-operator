# Bastet Operator

An interactive agent for analyzing bug bounty opportunities, part of the [Bastet](https://bastet.ai) suite of security tools.

## Overview

Bastet Operator is an intelligent automation tool designed to streamline and enhance bug bounty hunting workflows. As a core component of the Bastet ecosystem, it provides researchers with an interactive agent capable of analyzing targets, identifying potential vulnerabilities, and orchestrating comprehensive security assessments.

### Directory Structure

Bastet Operator operates from four main directories:

- **`targets/`** - MkDocs wiki containing target lists and interesting observations within scope ([bastet-targets](https://github.com/bastet-ai/bastet-targets/))
- **`wisdom/`** - Knowledge base where Bastet records learnings from security scanning tools ([bastet-wisdom](https://github.com/bastet-ai/bastet-wisdom))
- **`tools/`** - Custom Python tools for data interaction and analysis
- **`logs/`** - Tool output, session summaries, and operational data (gitignored, local only)

## Key Features

- 🎯 **Intelligent Target Analysis** - Automated reconnaissance and attack surface mapping
- 🔍 **Vulnerability Detection** - AI-powered identification of security weaknesses
- 🤖 **Interactive Agent** - Conversational interface for guided security testing
- 📊 **Opportunity Assessment** - Smart prioritization of bug bounty targets
- 🔗 **Bastet Integration** - Seamless workflow with other Bastet suite tools
- 📈 **Continuous Monitoring** - Real-time tracking of target changes and new opportunities

## The Bastet Suite

Bastet Operator is part of the comprehensive Bastet security platform available at [bastet.ai](https://bastet.ai). The suite provides:

- **Bastet Core** - Central intelligence and coordination engine
- **Bastet Operator** - Interactive bug bounty analysis agent (this project)
- **Bastet Scanner** - Automated vulnerability scanning capabilities
- **Bastet Intelligence** - Threat intelligence and data aggregation
- **Bastet Workflow** - Security testing automation and orchestration

## Getting Started

### Prerequisites

- Python 3.8+
- Docker (optional, for containerized deployment)
- Valid Bastet platform credentials

### Installation

```bash
# Clone the main repository
git clone https://github.com/bastet-ai/bastet-operator.git
cd bastet-operator

# Clone the remote wikis
git clone https://github.com/bastet-ai/bastet-targets.git targets
git clone https://github.com/bastet-ai/bastet-wisdom.git wisdom

# Create local directories
mkdir -p tools logs

# Install dependencies
pip install -r requirements.txt

# Configure your Bastet credentials
cp config/config.example.yaml config/config.yaml
# Edit config.yaml with your settings
```

### Quick Start

```bash
# Start the Bastet Operator
python bastet_operator.py

# Or using Docker
docker run -it bastet/operator:latest
```

## Usage

### Interactive Mode

Launch Bastet Operator in interactive mode to begin analyzing bug bounty opportunities:

```bash
bastet-operator --interactive
```

### Target Analysis

```bash
# Analyze a specific target
bastet-operator analyze --target example.com

# Bulk analysis from file
bastet-operator analyze --targets targets.txt

# Continuous monitoring
bastet-operator monitor --target example.com --interval 1h
```

### Integration with Bastet Platform

Bastet Operator seamlessly integrates with the broader Bastet ecosystem:

```python
from bastet_operator import Agent

# Initialize the operator
agent = Agent(api_key="your_bastet_api_key")

# Analyze opportunities
opportunities = agent.analyze_target("example.com")

# Get AI-powered recommendations
recommendations = agent.get_recommendations(opportunities)
```

## Configuration

Configure Bastet Operator through the `config/config.yaml` file:

```yaml
bastet:
  api_key: "your_api_key"
  endpoint: "https://api.bastet.ai"
  
operator:
  max_concurrent_scans: 5
  output_format: "json"
  
targets:
  timeout: 30
  user_agent: "Bastet-Operator/1.0"
```

## Bug Bounty Workflow

Bastet Operator enhances your bug bounty process through its integrated directory system:

1. **Target Management** (`targets/`) - Document and track bug bounty targets with detailed scope observations
2. **Knowledge Building** (`wisdom/`) - Accumulate security testing methodologies and tool learnings  
3. **Tool Development** (`tools/`) - Create and maintain custom Python tools for specific testing needs
4. **Session Tracking** (`logs/`) - Record all tool output, findings, and interactive session summaries
5. **Continuous Learning** - Sync knowledge and targets across the distributed Bastet ecosystem

### Workflow Integration

- **Interactive Sessions**: All conversations and findings are automatically summarized in `logs/`
- **Target Documentation**: Interesting observations are recorded in the `targets/` wiki
- **Methodology Refinement**: Successful techniques are documented in the `wisdom/` knowledge base
- **Tool Evolution**: Custom scripts and utilities are versioned in `tools/`

## Contributing

We welcome contributions to Bastet Operator! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Format code
black bastet_operator/
flake8 bastet_operator/
```

## Documentation

- [API Documentation](docs/api.md)
- [User Guide](docs/user-guide.md)
- [Integration Examples](docs/examples/)
- [Bastet Platform Docs](https://docs.bastet.ai)

## Security

Bastet Operator is designed with security as a priority:

- 🔐 **Encrypted Communications** - All API communications use TLS 1.3
- 🛡️ **Secure Credential Storage** - API keys and sensitive data are encrypted at rest
- 🚫 **No Data Retention** - Target data is processed in memory and not stored
- ✅ **Regular Security Audits** - Continuous security assessment and updates

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📧 **Email**: support@bastet.ai
- 💬 **Discord**: [Bastet Community](https://discord.gg/bastet)
- 🐛 **Issues**: [GitHub Issues](https://github.com/bastet-ai/bastet-operator/issues)
- 📚 **Documentation**: [docs.bastet.ai](https://docs.bastet.ai)

## Acknowledgments

- Thanks to the bug bounty community for inspiration and feedback
- Built with modern AI/ML technologies for enhanced security testing
- Part of the broader Bastet ecosystem for comprehensive security automation

---

**Bastet Operator** - Intelligent bug bounty hunting, automated.

Visit [bastet.ai](https://bastet.ai) to learn more about the complete Bastet security platform.

