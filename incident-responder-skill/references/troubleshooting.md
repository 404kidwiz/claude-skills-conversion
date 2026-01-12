# Incident Responder - Troubleshooting

This guide helps troubleshoot common issues when using incident responder automation scripts and incident management workflows.

## Script Execution Issues

### Python Scripts Not Found

**Problem**: `python scripts/incident_triage.py` returns "No such file or directory"

**Solutions**:
- Verify you're in the correct directory: `cd incident-responder-skill`
- Check scripts directory exists: `ls scripts/`
- Ensure Python 3.7+ is installed: `python --version`

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'json'` or other import errors

**Solutions**:
- Ensure using Python 3: `python3 scripts/incident_triage.py`
- Install required dependencies: `pip install -r requirements.txt` (if requirements.txt exists)

### Permission Denied

**Problem**: `PermissionError: [Errno 13] Permission denied` when writing output files

**Solutions**:
- Check file permissions: `ls -la scripts/`
- Make scripts executable: `chmod +x scripts/*.py`
- Use sudo if necessary (not recommended): `sudo python scripts/incident_triage.py`

## Incident Triage Issues

### Incorrect Severity Classification

**Problem**: Incident classified as wrong severity level

**Solutions**:
- Verify impact type matches expected values
- Check urgency parameter is valid
- Review affected_users count is not zero
- Example: `python scripts/incident_triage.py --incident INC-001 --impact service_outage --urgency immediate --affected-users 1000`

### Team Routing Not Working

**Problem**: Incorrect teams assigned to incident

**Solutions**:
- Verify severity level is recognized
- Check incident description keywords for type matching
- Review TEAM_MAPPING in IncidentClassifier class
- Customize team mapping if needed

### Evidence Collection Fails

**Problem**: No metrics or logs collected in triage report

**Solutions**:
- Provide service name: `--service api-service`
- Verify monitoring integration is available
- Check network connectivity to monitoring services
- Review EvidenceCollector configuration

## Incident Analysis Issues

### Log Correlation Empty

**Problem**: Correlated logs return no results

**Solutions**:
- Verify start_time and end_time are valid ISO format
- Ensure time range includes incident period
- Check log sources are accessible
- Provide valid incident_id for log lookup

### Metrics Not Found

**Problem**: Metric analysis shows all zeros

**Solutions**:
- Verify service name is correct
- Ensure metrics collection is running
- Check Prometheus/DataDog/CloudWatch integration
- Review time window matches incident period

### Root Cause Not Detected

**Problem**: Root cause analysis returns no causes

**Solutions**:
- Provide error logs via manual input or file
- Verify log format is compatible
- Check error patterns in ROOT_CAUSE_PATTERNS
- Add custom error patterns if needed

## Incident Response Issues

### Containment Actions Fail

**Problem**: Containment action not executed

**Solutions**:
- Verify action name is valid: `isolate_service`, `revoke_credentials`, `block_traffic`, `shutdown_system`
- Check target system is accessible
- Verify network/firewall permissions
- Review execution logs for error messages

### Mitigation Actions Not Applied

**Problem**: Mitigation not working as expected

**Solutions**:
- Verify action is valid: `enable_circuit_breaker`, `scale_up`, `degrade_service`, `switch_to_backup`
- Check service supports mitigation type
- Verify infrastructure is accessible
- Review mitigation steps for manual intervention

### Team Notifications Not Sent

**Problem**: Teams not receiving notifications

**Solutions**:
- Verify team names are correct
- Check Slack/PagerDuty integration
- Verify notification channels exist
- Test with `--teams devops-incident-responder security-engineer`

## Runbook Generation Issues

### Unknown Incident Type

**Problem**: `ValueError: Unknown incident type`

**Solutions**:
- Verify incident_type is in allowed list: `data_breach`, `service_outage`, `security_violation`, `database_failure`, `network_incident`
- Check spelling and case sensitivity
- Review IncidentTypeLibrary.INCIDENT_TYPES for available types

### Markdown Generation Fails

**Problem`: Markdown output file not created

**Solutions**:
- Use `--markdown` flag: `--markdown output.md`
- Or use `--format both` for both JSON and Markdown
- Verify output directory is writable
- Check markdown_content generation in script

## Maintenance Automation Issues

### Backup Fails

**Problem**: Backup creation returns errors

**Solutions**:
- Verify system name is correct
- Check backup type: `full`, `incremental`, `differential`
- Verify storage location has sufficient space
- Check backup service connectivity

### Health Validation Fails

**Problem**: System health validation shows issues

**Solutions**:
- Review specific health check failures
- Check resource limits (CPU, memory, disk)
- Verify services are running
- Validate network connectivity

## Common Issues Across All Scripts

### JSON Parsing Errors

**Problem**: Invalid JSON in output files

**Solutions**:
- Verify no syntax errors in script
- Check for special characters in output
- Use JSON validator tool to verify output
- Report bug if persistent

### Logging Issues

**Problem**: No logs or incorrect log levels

**Solutions**:
- Set logging level: `--log-level DEBUG`
- Check log file permissions
- Verify logging configuration in script
- Use `--verbose` flag if available

### Time Zone Issues

**Problem**: Timestamps in wrong time zone

**Solutions**:
- Scripts use UTC by default
- Convert to local time for display
- Use datetime library for conversions
- Verify system time is correct

## Performance Issues

### Script Execution Slow

**Problem**: Scripts taking too long to execute

**Solutions**:
- Reduce time window for log/metric collection
- Use parallel processing if available
- Limit number of services analyzed
- Cache frequently accessed data

### Memory Issues

**Problem**: `MemoryError: Unable to allocate array`

**Solutions**:
- Reduce batch size for processing
- Limit log entries processed
- Increase system memory
- Use streaming for large datasets

## Integration Issues

### Slack Integration Not Working

**Problem**: Notifications not reaching Slack

**Solutions**:
- Verify Slack webhook URL is correct
- Check webhook permissions
- Test webhook with curl command
- Review Slack app configuration

### PagerDuty Integration Fails

**Problem**: Incidents not creating in PagerDuty

**Solutions**:
- Verify API key is valid
- Check service name in PagerDuty
- Test API connectivity
- Review PagerDuty integration logs

### Status Page Updates Fail

**Problem**: Status page not updating

**Solutions**:
- Verify status page provider (Statuspage.io, etc.)
- Check API credentials
- Test API with curl command
- Review status page configuration

## Debug Mode

### Enable Debug Logging

```bash
# Set environment variable
export DEBUG=true

# Or modify script logging level
logging.basicConfig(level=logging.DEBUG)
```

### Dry Run Mode

```bash
# Test without making changes
python scripts/incident_triage.py --incident TEST-001 --dry-run
```

### Verbose Output

```bash
# Get detailed output
python scripts/incident_response.py --incident INC-001 --action-type containment --verbose
```

## Getting Help

### Script Help

```bash
# Get help for any script
python scripts/incident_triage.py --help
python scripts/incident_analysis.py --help
python scripts/incident_response.py --help
python scripts/runbook_generator.py --help
python scripts/maintenance_automation.py --help
```

### Error Messages

- Read error messages carefully
- Check logs for full stack traces
- Search error codes in documentation
- Review recent changes to environment

### Common Error Codes

- `E001`: Configuration file not found
- `E002`: Invalid input parameter
- `E003`: Service connection failed
- `E004`: Permission denied
- `E005`: Timeout exceeded

## Prevention

### Regular Testing

- Test scripts in non-production environment first
- Verify all integrations are working
- Run sample incidents to validate workflows
- Check output files for expected format

### Documentation

- Keep runbooks up to date
- Document custom configurations
- Track changes to scripts
- Share lessons learned with team

### Monitoring

- Monitor script execution time
- Alert on script failures
- Track resource usage
- Review logs regularly
