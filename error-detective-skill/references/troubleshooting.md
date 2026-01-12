# Error Detective - Troubleshooting

This guide helps troubleshoot common issues when using error detection automation scripts and analyzing error patterns.

## Script Execution Issues

### Python Scripts Not Found

**Problem**: `python scripts/error_detection_automation.py` returns "No such file or directory"

**Solutions**:
- Verify you're in the correct directory: `cd error-detective-skill`
- Check scripts directory exists: `ls scripts/`
- Ensure Python 3.7+ is installed: `python --version`

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'json'` or other import errors

**Solutions**:
- Ensure using Python 3: `python3 scripts/error_detection_automation.py`
- Install required dependencies if requirements.txt exists

### Permission Denied

**Problem**: `PermissionError: [Errno 13] Permission denied` when writing output files

**Solutions**:
- Check file permissions: `ls -la scripts/`
- Make scripts executable: `chmod +x scripts/*.py`
- Verify write permissions for output directory

## Log Scanning Issues

### No Errors Found

**Problem**: Log scan returns zero errors

**Solutions**:
- Verify log entries are provided
- Check log format matches expected patterns
- Review error patterns in ERROR_PATTERNS
- Add custom patterns if your logs use different formats
- Use `--sample-logs` to test with sample data

### Incorrect Error Severity

**Problem**: Errors classified as wrong severity level

**Solutions**:
- Review error patterns in LogScanner.ERROR_PATTERNS
- Adjust pattern matching rules if needed
- Check log message content for pattern keywords
- Verify severity mapping is appropriate

### Pattern Matching Issues

**Problem**: Expected errors not being detected

**Solutions**:
- Check case sensitivity (patterns are case-insensitive)
- Verify regex patterns match your log format
- Add custom patterns to ERROR_PATTERNS
- Test pattern matching with sample logs

## Error Correlation Issues

### No Correlated Incidents

**Problem**: Correlation returns zero incidents

**Solutions**:
- Provide at least 2 services for correlation
- Verify time windows overlap across services
- Check error timestamps are in valid ISO format
- Ensure errors exist in time window

### Cascade Detection Fails

**Problem**: Error cascades not being identified

**Solutions**:
- Review cascade detection logic in _find_cascade_between_services()
- Adjust time window for cascade detection (currently 60 seconds)
- Increase sensitivity if cascades are being missed
- Check error severity classification

### Timeline Construction Issues

**Problem**: Error timeline not being built correctly

**Solutions**:
- Verify timestamp extraction from logs
- Check timestamp format is recognized
- Review _create_time_windows() logic
- Adjust time window size (currently 5 minutes)

## Anomaly Detection Issues

### Insufficient Data Error

**Problem**: `Insufficient data for anomaly detection`

**Solutions**:
- Provide at least 10 data points for analysis
- Increase error_history length
- Verify error rate data is available
- Use historical data for better baseline

### Too Many False Positives

**Problem**: Many anomalies detected that aren't real issues

**Solutions**:
- Adjust threshold multiplier (currently 2 standard deviations)
- Increase to 2.5 or 3 for less sensitivity
- Review baseline calculation logic
- Consider different detection algorithms

### Too Few Anomalies

**Problem**: Real anomalies not being detected

**Solutions**:
- Decrease threshold multiplier to 1.5 or 1
- Review data for actual anomalies
- Check standard deviation calculation
- Adjust time window for baseline

## Common Issues Across All Scripts

### JSON Output Errors

**Problem**: Invalid JSON in output files

**Solutions**:
- Verify no syntax errors in script
- Check for special characters in output
- Use JSON validator tool to verify output
- Check for memory issues during generation

### Time Zone Confusion

**Problem**: Timestamps in wrong time zone

**Solutions**:
- Scripts use UTC by default
- Convert to local time for display
- Verify system time is correct
- Check time zone configuration

### Performance Issues

**Problem**: Scripts taking too long to execute

**Solutions**:
- Reduce number of logs to scan
- Limit number of services analyzed
- Use parallel processing if available
- Reduce time windows for correlation

## Integration Issues

### Log Source Connection Fails

**Problem**: Cannot read logs from log aggregation system

**Solutions**:
- Verify connection to ELK, Splunk, or Loki
- Check API credentials are valid
- Test query directly with API
- Review service discovery configuration

### Monitoring Integration Issues

**Problem**: Metrics not being collected for anomaly detection

**Solutions**:
- Verify monitoring system is running
- Check API endpoints are accessible
- Test query directly: `curl http://prometheus:9090/api/v1/query`
- Review service discovery configuration

### Alerting Integration Fails

**Problem**: Alerts not triggered on detected anomalies

**Solutions**:
- Verify alerting system configuration
- Check webhook URLs are correct
- Test alert generation manually
- Review alert rules and thresholds

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
# Test without actual processing
python scripts/error_detection_automation.py --scan --services api-service database-service --dry-run
```

### Verbose Output

```bash
# Get detailed execution information
python scripts/error_detection_automation.py --scan --services api-service --verbose
```

### Sample Logs Generation

```bash
# Generate sample logs for testing
python scripts/error_detection_automation.py --sample-logs --error-count 50
```

## Getting Help

### Script Help

```bash
# Get help for the script
python scripts/error_detection_automation.py --help
```

### Error Messages

- Read error messages carefully
- Check logs for full stack traces
- Search error codes in documentation
- Review recent changes to environment

### Common Error Codes

- `E001`: Log parsing failed
- `E002`: Pattern matching error
- `E003`: Correlation timeout
- `E004`: Insufficient data for analysis
- `E005`: Anomaly detection threshold error

## Prevention

### Pre-Deployment Checklist

- [ ] Test log scanning with sample data
- [ ] Verify error patterns match your log format
- [ ] Test correlation with multiple services
- [ ] Validate anomaly detection baseline
- [ ] Check integration with monitoring systems
- [ ] Test alert generation

### Monitoring Setup

- Set up alerts for error rate increases
- Configure dashboards for error visualization
- Monitor script execution time
- Track false positive rates
- Review detected anomalies regularly

### Data Management

- Archive historical error data
- Clean up old logs to maintain performance
- Maintain error pattern library
- Update patterns as systems evolve
- Regularly review and tune thresholds

## Best Practices Summary

- Start with sample logs to test functionality
- Use appropriate time windows for your incident patterns
- Tune anomaly detection thresholds for your environment
- Integrate with existing monitoring and alerting
- Review and update error patterns regularly
- Validate findings with incident data
- Build knowledge base of common error patterns
- Use automation to scale analysis across many services
