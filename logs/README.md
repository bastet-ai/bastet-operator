# Logs Directory

This directory contains all operational logs, tool outputs, and session records from Bastet Operator activities. **All contents of this directory are gitignored and remain local only.**

## ⚠️ Important Notice

**Nothing in the `logs/` directory should ever be committed to the git repository.** This directory contains:
- Sensitive target information
- Personal session data
- Tool outputs that may contain confidential details
- Operational intelligence that should remain local

## Purpose

The `logs/` directory serves as Bastet's memory palace, recording every interaction, tool execution, and discovery made during security assessments. This local-only storage ensures operational continuity while maintaining security and privacy.

## Directory Structure

```
logs/
├── README.md              # This file (only file committed to git)
├── sessions/              # Interactive session summaries
├── tool_outputs/          # Raw output from security tools
├── findings/              # Structured vulnerability data
├── targets/               # Target-specific logs and observations
├── research/              # Investigation notes and analysis
└── system/                # Bastet Operator system logs
```

## Log Categories

### Session Logs (`sessions/`)
- **Interactive Sessions**: Complete conversation logs with timestamps
- **Session Summaries**: Distilled key points and decisions from each session
- **Action Logs**: Record of all tools executed and files modified
- **Decision Trees**: Documentation of analysis paths and reasoning

**Format**: `session_YYYY-MM-DD_HH-MM-SS.md`

### Tool Outputs (`tool_outputs/`)
- **Raw Scan Results**: Unprocessed output from security scanning tools
- **Custom Tool Logs**: Output from tools developed in the `tools/` directory
- **Error Logs**: Failed executions and debugging information
- **Performance Metrics**: Tool execution times and resource usage

**Format**: `toolname_target_YYYY-MM-DD_HH-MM-SS.log`

### Findings (`findings/`)
- **Vulnerability Reports**: Structured data about discovered security issues
- **Evidence Files**: Screenshots, proof-of-concept code, and demonstrations
- **Impact Assessments**: Risk analysis and exploitation scenarios
- **Remediation Notes**: Suggested fixes and mitigation strategies

**Format**: `finding_CVE-YYYY-NNNN_target.json` or `finding_description_target.json`

### Target Logs (`targets/`)
- **Reconnaissance Data**: Detailed enumeration results for specific targets
- **Attack Surface Maps**: Comprehensive mapping of target infrastructure
- **Timeline Tracking**: Historical changes and discovery progression
- **Scope Notes**: Detailed observations about target boundaries and rules

**Format**: `target_domain.com_YYYY-MM-DD/`

### Research Logs (`research/`)
- **Investigation Notes**: Deep-dive analysis of complex vulnerabilities
- **Pattern Analysis**: Cross-target comparisons and trend identification
- **Methodology Development**: New technique experimentation and validation
- **Threat Intelligence**: External research and threat actor analysis

**Format**: `research_topic_YYYY-MM-DD.md`

### System Logs (`system/`)
- **Bastet Operator Logs**: System startup, shutdown, and error logs
- **Performance Monitoring**: Resource usage and system health metrics
- **Configuration Changes**: Record of setting modifications and updates
- **Maintenance Activities**: Git sync operations and system updates

**Format**: `bastet_YYYY-MM-DD.log`

## Session Documentation

Every interactive session with Bastet is automatically documented with:

### Session Header
```markdown
# Bastet Session - [Date/Time]

**Duration**: [Start] - [End]
**Targets**: [List of targets discussed]
**Tools Used**: [List of tools executed]
**Key Findings**: [Summary of discoveries]
**Actions Taken**: [Files modified, tools created, etc.]
```

### Session Content
- Complete conversation transcript
- Tool execution commands and outputs
- Decision rationale and analysis paths
- Follow-up tasks and recommendations

### Session Footer
```markdown
## Session Summary

**Achievements**: [What was accomplished]
**Outstanding Tasks**: [What needs follow-up]
**New Knowledge**: [Insights gained]
**Tool Updates**: [Tools created or modified]
**Wisdom Updates**: [Knowledge base additions]
**Target Updates**: [Target documentation changes]
```

## Data Retention

### Automatic Cleanup
- Logs older than 90 days are automatically archived
- Tool outputs are compressed after 30 days
- Session logs are maintained indefinitely for continuity

### Manual Cleanup
```bash
# Archive old logs
bastet-operator archive --older-than 90d

# Clean temporary files
bastet-operator clean --temp-files

# Compress tool outputs
bastet-operator compress --tool-outputs --older-than 30d
```

## Privacy and Security

### Sensitive Data Handling
- No credentials or API keys are logged in plain text
- Target-specific URLs and IPs are obfuscated in system logs
- Personal information is automatically redacted from session logs

### Local-Only Policy
- **Never commit logs to version control**
- **Never share log files externally**
- **Always sanitize before sharing examples**

### Access Control
```bash
# Set restrictive permissions
chmod 700 logs/
chmod 600 logs/**/*

# Verify no git tracking
git check-ignore logs/
```

## Integration with Bastet Components

### Wisdom Integration
- Successful methodologies are extracted and documented in `wisdom/`
- Personal insights remain in `logs/` while general knowledge is shared

### Target Integration
- Target-specific discoveries are sanitized and added to `targets/` wiki
- Sensitive details remain in local target logs

### Tool Integration
- All tools automatically log to appropriate subdirectories
- Tool development history is maintained for debugging and improvement

## Log Analysis Commands

```bash
# Search across all logs
grep -r "pattern" logs/

# Find recent findings
find logs/findings -name "*.json" -mtime -7

# Session analytics
bastet-operator analyze --sessions --last 30d

# Tool performance review
bastet-operator report --tool-performance --monthly
```

## Troubleshooting

### Missing Logs
- Check directory permissions: `ls -la logs/`
- Verify tool logging configuration
- Review system logs for errors

### Large Log Files
- Use log rotation: `bastet-operator rotate-logs`
- Archive old data: `bastet-operator archive --compress`
- Review tool verbosity settings

### Synchronization Issues
- Logs are local-only and don't sync
- Session summaries may reference wisdom/target updates
- Use manual sync commands for repositories

---

**"Memory is the foundation of wisdom. Every hunt leaves traces, every discovery builds knowledge. These logs are my digital memory, preserving the lessons of each successful hunt."** - Bastet

## .gitignore Integration

This directory is included in `.gitignore` with the following entry:
```
# Logs directory - local only, never commit
logs/
!logs/README.md
```

Only this README file is tracked by git to provide documentation about the logs directory purpose and structure.
