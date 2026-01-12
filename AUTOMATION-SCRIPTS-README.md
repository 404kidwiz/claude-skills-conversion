# Automation Scripts README

This document provides a comprehensive guide to all automation scripts created for the Claude Skills Conversion project. These scripts enhance the capabilities of various skills by providing executable automation for common tasks.

## Table of Contents

- [Directory Structure](#directory-structure)
- [Scripts by Skill](#scripts-by-skill)
- [Usage Examples](#usage-examples)
- [Best Practices](#best-practices)
- [Extension and Maintenance](#extension-and-maintenance)
- [Troubleshooting](#troubleshooting)

## Directory Structure

```
claude-skills-conversion/
├── incident-responder-skill/
│   ├── SKILL.md
│   ├── scripts/
│   │   ├── incident_triage.py
│   │   ├── incident_analysis.py
│   │   ├── incident_response.py
│   │   ├── runbook_generator.py
│   │   ├── maintenance_automation.py
│   │   └── handle_alerts.py (existing)
│   └── references/
│       ├── troubleshooting.md
│       └── best_practices.md
│
├── chaos-engineer-skill/
│   ├── SKILL.md
│   ├── scripts/
│   │   ├── chaos_experiment.py
│   │   └── resilience_assessment.py
│   └── references/
│       ├── troubleshooting.md
│       └── best_practices.md
│
├── error-detective-skill/
│   ├── SKILL.md
│   ├── scripts/
│   │   └── error_detection_automation.py
│   └── references/
│       ├── troubleshooting.md
│       └── best_practices.md
│
├── backend-developer-skill/
│   ├── SKILL.md
│   ├── scripts/
│   │   ├── scaffold_api.py (existing)
│   │   ├── generate_model.py (existing)
│   │   ├── setup_auth.py (existing)
│   │   ├── create_middleware.py (existing)
│   │   ├── error_handler.py (existing)
│   │   ├── setup_logging.py (existing)
│   │   ├── generate_docs.py (existing)
│   │   ├── create_tests.py (existing)
│   │   └── deploy.sh (existing)
│   └── references/
│       ├── troubleshooting.md
│       └── best_practices.md
│
└── build-engineer-skill/
    ├── SKILL.md
    ├── scripts/
    │   ├── config_webpack.py (existing)
    │   ├── config_vite.py (existing)
    │   ├── optimize_cache.py (existing)
    │   ├── code_splitting.py (existing)
    │   ├── dev_server.py (existing)
    │   └── optimize_production.py (existing)
    └── references/
        ├── troubleshooting.md
        └── best_practices.md
```

## Scripts by Skill

### Incident Responder Skill

#### `incident_triage.py`

**Purpose**: Automates initial incident triage by classifying severity, routing to teams, and collecting initial evidence.

**Usage**:
```bash
python scripts/incident_triage.py --incident INC-001 --description "Service outage" \
  --impact service_outage --urgency immediate --affected-users 500 \
  --service api-service --output triage_report.json
```

**Key Features**:
- Automated severity classification (CRITICAL, HIGH, MEDIUM, LOW)
- Team routing based on incident type and severity
- Initial metrics and evidence collection
- Comprehensive triage report generation

**Output**: JSON triage report with classification, assigned teams, metrics, and recommended actions.

---

#### `incident_analysis.py`

**Purpose**: Performs deep incident analysis by correlating logs/metrics, identifying root causes, and measuring business impact.

**Usage**:
```bash
python scripts/incident_analysis.py --incident INC-001 \
  --start-time "2024-01-12T10:00:00Z" \
  --end-time "2024-01-12T11:30:00Z" \
  --affected-users 500 --downtime 90 \
  --service api-service --output analysis_report.json
```

**Key Features**:
- Log correlation across multiple services
- Metric analysis for anomalies and trends
- Business impact calculation (revenue, SLA, users)
- Root cause pattern analysis

**Output**: JSON analysis report with correlation, metrics, impact, root causes, and recommendations.

---

#### `incident_response.py`

**Purpose**: Automates incident response actions including containment, mitigation, team coordination, and progress tracking.

**Usage**:
```bash
# Containment action
python scripts/incident_response.py --incident INC-001 --severity critical \
  --action-type containment --action isolate_service --target api-service

# Team notification
python scripts/incident_response.py --incident INC-001 --severity critical \
  --action-type notify --teams security-engineer devops-incident-responder

# Status update
python scripts/incident_response.py --incident INC-001 --severity critical \
  --action-type status --status investigating --details "Root cause identified"
```

**Key Features**:
- Predefined containment and mitigation actions
- Automated team notification
- Status update tracking
- Response timeline and audit trail

**Output**: JSON response report with executed actions, team notifications, and current status.

---

#### `runbook_generator.py`

**Purpose**: Generates comprehensive incident response runbooks with procedures, team contacts, and communication templates.

**Usage**:
```bash
# Generate JSON runbook
python scripts/runbook_generator.py --incident-type service_outage \
  --title "Service Outage Response Runbook" \
  --output service_outage_runbook.json

# Generate Markdown runbook
python scripts/runbook_generator.py --incident-type data_breach \
  --format both --markdown data_breach_runbook.md \
  --output data_breach_runbook.json
```

**Key Features**:
- 5 incident types: data_breach, service_outage, security_violation, database_failure, network_incident
- Complete response procedures for each phase
- Team contacts and escalation paths
- Communication templates (internal, customer, executive)
- JSON and Markdown output formats

**Output**: Comprehensive runbook in JSON and/or Markdown format.

---

#### `maintenance_automation.py`

**Purpose**: Automates system maintenance tasks including scheduling, backups, notifications, and health validation.

**Usage**:
```bash
python scripts/maintenance_automation.py --task system_update \
  --system api-service --start-time "2024-01-20T02:00:00Z" \
  --duration 120 --priority medium --backup-type full \
  --affected-users 0 --output maintenance_report.json
```

**Key Features**:
- Maintenance window scheduling
- Backup plan creation (full, incremental, differential)
- Stakeholder notification generation
- Maintenance task execution
- Post-maintenance health validation

**Output**: JSON maintenance report with window, execution, validation, and recommendations.

---

### Chaos Engineer Skill

#### `chaos_experiment.py`

**Purpose**: Automates chaos engineering experiments with hypothesis design, failure injection, and automated rollback.

**Usage**:
```bash
python scripts/chaos_experiment.py --experiment database-failure-test \
  --target database-service --failure-type pod_kill \
  --blast-radius 5 --duration 15 \
  --output chaos_experiment_report.json
```

**Key Features**:
- 8 failure types: pod_kill, network_latency, packet_loss, network_partition, cpu_stress, memory_stress, disk_failure, dns_failure
- Hypothesis-driven experiment design
- Blast radius control (percentage of traffic/users)
- Automated rollback with 30-second target
- Metrics collection (before, during, after)
- Experiment report with validation and lessons learned

**Output**: JSON experiment report with design, injection, metrics, hypothesis validation, and recommendations.

---

#### `resilience_assessment.py`

**Purpose**: Evaluates system resilience by analyzing patterns, identifying SPOFs, testing failover, and assessing capacity.

**Usage**:
```bash
python scripts/resilience_assessment.py --target api-service \
  --component database --output resilience_report.json
```

**Key Features**:
- Resilience pattern analysis (circuit breaker, retry, bulkhead, timeout, fallback)
- Single Point of Failure (SPOF) identification
- Failover capability testing
- Capacity analysis and headroom calculation
- Overall resilience score (0-100%)
- Priority improvement roadmap

**Output**: JSON assessment report with patterns, SPOFs, failover, capacity, score, and improvements.

---

### Error Detective Skill

#### `error_detection_automation.py`

**Purpose**: Automates error detection and analysis by scanning logs, correlating across services, and detecting anomalies.

**Usage**:
```bash
# Scan logs for errors
python scripts/error_detection_automation.py --scan \
  --services api-service database-service auth-service \
  --output error_detection_report.json

# Use sample logs for testing
python scripts/error_detection_automation.py --scan \
  --sample-logs --error-count 50 --output test_report.json

# Correlate errors
python scripts/error_detection_automation.py --correlate \
  --services api-service database-service

# Detect anomalies
python scripts/error_detection_automation.py --detect-anomalies \
  --service api-service --output anomaly_report.json
```

**Key Features**:
- Log scanning with error pattern matching (critical, high, medium severity)
- Error correlation across multiple services
- Anomaly detection using statistical analysis (mean ± 2 standard deviations)
- Top error pattern identification
- Error cascade detection
- Comprehensive error detection report

**Output**: JSON report with scanned services, correlated incidents, detected anomalies, and recommendations.

---

## Usage Examples

### Incident Response Workflow

Complete incident management workflow:

```bash
# 1. Triage the incident
python scripts/incident_triage.py \
  --incident INC-001 \
  --description "API service experiencing 503 errors" \
  --impact service_outage \
  --urgency immediate \
  --affected-users 1000 \
  --service api-service \
  --output triage.json

# 2. Contain the issue
python scripts/incident_response.py \
  --incident INC-001 \
  --severity critical \
  --action-type containment \
  --action enable_circuit_breaker \
  --target upstream-service

# 3. Analyze root cause
python scripts/incident_analysis.py \
  --incident INC-001 \
  --start-time "2024-01-12T10:00:00Z" \
  --end-time "2024-01-12T11:00:00Z" \
  --affected-users 1000 \
  --downtime 60 \
  --service api-service \
  --output analysis.json

# 4. Notify teams
python scripts/incident_response.py \
  --incident INC-001 \
  --severity critical \
  --action-type notify \
  --teams security-engineer devops-incident-responder backend-developer

# 5. Update status
python scripts/incident_response.py \
  --incident INC-001 \
  --severity critical \
  --action-type status \
  --status resolved \
  --details "Root cause fixed and service restored"
```

### Chaos Engineering Workflow

Complete chaos engineering workflow:

```bash
# 1. Assess current resilience
python scripts/resilience_assessment.py \
  --target api-service \
  --component database \
  --output baseline_resilience.json

# 2. Design and run chaos experiment
python scripts/chaos_experiment.py \
  --experiment database-failure-resilience \
  --target database-service \
  --failure-type pod_kill \
  --blast-radius 5 \
  --output experiment.json

# 3. Analyze experiment results
# Review experiment.json for hypothesis validation
# Check lessons learned and recommendations

# 4. Re-assess resilience after improvements
python scripts/resilience_assessment.py \
  --target api-service \
  --output post_experiment_resilience.json

# 5. Compare scores
# baseline_resilience.json vs post_experiment_resilience.json
# Measure improvement in resilience score
```

### Error Detection Workflow

Complete error detection workflow:

```bash
# 1. Scan logs across services
python scripts/error_detection_automation.py --scan \
  --services api-service database-service auth-service cache-service \
  --output error_scan.json

# 2. Correlate errors
python scripts/error_detection_automation.py --correlate \
  --services api-service database-service \
  --output correlation.json

# 3. Detect anomalies
python scripts/error_detection_automation.py --detect-anomalies \
  --service api-service \
  --output anomalies.json

# 4. Review findings
# Check error_scan.json for top error patterns
# Check correlation.json for cascades
# Check anomalies.json for unexpected behavior
```

## Best Practices

### General Script Usage

1. **Always Test First**: Run scripts with sample data before production use
2. **Use Version Control**: Track changes to scripts and configurations
3. **Check Output**: Verify generated files contain expected data
4. **Handle Errors**: Review error messages and check troubleshooting guides
5. **Document Customizations**: Keep records of any modifications made

### Incident Response

- **Respond Rapidly**: Use triage script immediately upon detection
- **Contain First**: Execute containment actions before full analysis
- **Preserve Evidence**: Never modify systems before collecting evidence
- **Communicate Regularly**: Update stakeholders throughout the incident
- **Document Everything**: Maintain timeline of all actions and decisions
- **Learn Continuously**: Update runbooks based on every incident

### Chaos Engineering

- **Hypothesis First**: Always start with a clear, testable hypothesis
- **Start Small**: Begin with low blast radius (1-5% in production)
- **Monitor Continuously**: Watch metrics in real-time during experiments
- **Rollback Ready**: Have automated rollback tested before starting
- **Learn from All**: Even failed experiments provide insights
- **Iterate Gradually**: Increase complexity only as confidence builds

### Error Detection

- **Correlate Across Services**: Don't analyze in isolation
- **Establish Baselines**: Use historical data for anomaly detection
- **Tune Thresholds**: Adjust for your environment to reduce false positives
- **Track Patterns**: Build knowledge base of common error patterns
- **Automate Alerts**: Integrate with PagerDuty, Slack, etc.
- **Review Regularly**: Analyze error trends weekly/monthly

### Build Engineering

- **Optimize for Speed**: Enable caching and parallel processing
- **Analyze Bundle Sizes**: Regularly check for optimization opportunities
- **Test Locally First**: Verify build configurations before CI/CD
- **Monitor Build Times**: Alert on build time regressions
- **Keep Updated**: Update build tools regularly

## Extension and Maintenance

### Adding New Scripts

1. **Follow Existing Patterns**: Use similar structure and naming conventions
2. **Include Help Documentation**: Add `--help` support
3. **Error Handling**: Include try/except blocks with clear error messages
4. **Logging**: Use logging module with appropriate levels
5. **Type Hints**: Add type hints for better code clarity
6. **Docstrings**: Document function purposes and parameters

### Script Template

```python
#!/usr/bin/env python3
"""
[Script Description]

Automates [what this script does].

Usage:
    python scripts/script_name.py [OPTIONS]
    python scripts/script_name.py --help
"""

import argparse
import json
import logging
from typing import Dict, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='[Script description]')
    parser.add_argument('--option', help='Option description')
    parser.add_argument('--output', help='Output file path')
    
    args = parser.parse_args()
    
    # Script logic here
    logger.info("Executing script...")
    
    # Generate output
    result = {"status": "success", "data": "output"}
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        logger.info(f"Output saved to {args.output}")
    else:
        print(json.dumps(result, indent=2))
    
    logger.info("Script completed")

if __name__ == '__main__':
    main()
```

### Updating Existing Scripts

1. **Review Current Implementation**: Understand existing logic and patterns
2. **Test Changes**: Modify scripts and test thoroughly
3. **Update Documentation**: Keep SKILL.md and references in sync
4. **Version Control**: Commit changes with clear messages
5. **Notify Team**: Share significant changes with team

### Maintaining Reference Documentation

- **Update Troubleshooting**: Add new issues and solutions as discovered
- **Update Best Practices**: Incorporate lessons learned from usage
- **Keep in Sync**: Ensure SKILL.md sections match actual scripts
- **Review Regularly**: Monthly review of all documentation

## Troubleshooting

### Common Issues

#### Script Execution Fails

**Symptoms**: `No such file or directory`, `Permission denied`, or import errors

**Solutions**:
- Verify you're in the correct skill directory
- Check scripts directory exists
- Ensure Python 3.7+ is installed: `python --version`
- Make scripts executable: `chmod +x scripts/*.py`
- Check write permissions for output directory

#### Output Files Not Created

**Symptoms**: No output files generated, or files empty

**Solutions**:
- Verify output directory exists and is writable
- Check for error messages in script output
- Use absolute paths for output: `--output /full/path/to/output.json`
- Check available disk space
- Run with verbose flag if available

#### JSON Parsing Errors

**Symptoms**: `JSONDecodeError` when reading output files

**Solutions**:
- Verify script completed successfully
- Check for write errors during execution
- Validate JSON output with online validator
- Check for special characters in output

### Getting Help

#### Script Help

```bash
# Get help for any script
python scripts/script_name.py --help
```

#### Documentation

- SKILL.md: Overview and capabilities for each skill
- references/troubleshooting.md: Detailed troubleshooting guides
- references/best_practices.md: Best practices and recommendations

#### Debug Mode

```bash
# Enable debug logging
export DEBUG=true

# Or modify script
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

When contributing new scripts or improvements:

1. Follow existing code patterns and style
2. Include comprehensive documentation and examples
3. Test thoroughly across multiple scenarios
4. Update relevant SKILL.md files
5. Add to troubleshooting and best practices as needed
6. Submit with clear description of changes

## License

These automation scripts are part of the Claude Skills Conversion project. Refer to the main project LICENSE file for details.

## Support

For issues, questions, or contributions:
- Review this README for usage guidance
- Check skill-specific troubleshooting.md files
- Refer to SKILL.md files for capability descriptions
- Review best_practices.md for recommended approaches
