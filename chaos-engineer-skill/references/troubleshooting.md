# Chaos Engineer - Troubleshooting

This guide helps troubleshoot common issues when using chaos engineering automation scripts and conducting experiments.

## Script Execution Issues

### Python Scripts Not Found

**Problem**: `python scripts/chaos_experiment.py` returns "No such file or directory"

**Solutions**:
- Verify you're in the correct directory: `cd chaos-engineer-skill`
- Check scripts directory exists: `ls scripts/`
- Ensure Python 3.7+ is installed: `python --version`

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'json'` or other import errors

**Solutions**:
- Ensure using Python 3: `python3 scripts/chaos_experiment.py`
- Install required dependencies if requirements.txt exists

### Permission Denied

**Problem**: `PermissionError: [Errno 13] Permission denied` when executing scripts

**Solutions**:
- Check file permissions: `ls -la scripts/`
- Make scripts executable: `chmod +x scripts/*.py`
- Verify write permissions for output directory

## Chaos Experiment Issues

### Unknown Failure Type

**Problem**: `ValueError: Unknown failure type: xxx`

**Solutions**:
- Verify failure type is in allowed list: `pod_kill`, `network_latency`, `packet_loss`, `network_partition`, `cpu_stress`, `memory_stress`, `disk_failure`, `dns_failure`
- Check spelling and case sensitivity
- Review ExperimentDesigner.FAILURE_TYPES

### Blast Radius Issues

**Problem**: `ValueError: Blast radius must be between 0 and 100`

**Solutions**:
- Provide blast radius as percentage: `--blast-radius 10` for 10% of traffic
- Use recommended ranges:
  - Development: 100%
  - Staging: 50-100%
  - Production: 1-10%
- Never use 100% blast radius in production

### Hypothesis Not Validated

**Problem**: Experiment shows hypothesis invalidated

**Solutions**:
- Review steady state thresholds in experiment design
- Check if blast radius was too aggressive
- Verify metrics collection is working
- Consider reducing complexity of failure injection

### Rollback Fails

**Problem**: Rollback not completing successfully

**Solutions**:
- Verify system is still accessible
- Check network connectivity to target systems
- Review rollback steps in script
- Manual rollback if automated fails

## Resilience Assessment Issues

### Pattern Analysis Returns Low Score

**Problem**: Resilience score unexpectedly low

**Solutions**:
- Review pattern detection logic in _check_pattern_implementation()
- Verify system has required components installed
- Check if patterns are actually implemented in code
- Consider manual override for known patterns

### Single Points of Failure Not Detected

**Problem**: SPOF analysis misses known issues

**Solutions**:
- Review SPOF categories in SinglePointOfFailureAnalyzer
- Add custom SPOF items for your infrastructure
- Adjust detection logic in _check_spo_presence()
- Verify system configuration is accessible

### Failover Test Fails

**Problem**: Failover test shows all failures

**Solutions**:
- Verify failover infrastructure exists
- Check backup systems are running
- Review failover configuration
- Test failover procedures manually first

## Common Issues Across All Scripts

### Metrics Collection Fails

**Problem**: All metrics show zeros or "collection_initiated" status

**Solutions**:
- Verify monitoring system is accessible
- Check Prometheus/DataDog/CloudWatch integration
- Ensure service name is correct
- Test metrics API endpoints directly

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

## Performance Issues

### Script Execution Slow

**Problem**: Scripts taking too long to execute

**Solutions**:
- Reduce number of services analyzed
- Limit time window for metrics collection
- Use parallel processing if available
- Cache frequently accessed data

### Memory Errors

**Problem**: `MemoryError: Unable to allocate array`

**Solutions**:
- Reduce blast radius (less data to process)
- Limit number of services
- Increase system memory
- Use streaming for large datasets

## Integration Issues

### Kubernetes Integration Fails

**Problem**: Cannot inject pod kill or network failures in Kubernetes

**Solutions**:
- Verify kubectl configuration: `kubectl config current-context`
- Check RBAC permissions for chaos tool
- Verify cluster is accessible
- Test with simple command: `kubectl get pods`

### Monitoring Integration Issues

**Problem**: Metrics not being collected during experiments

**Solutions**:
- Verify monitoring system is running
- Check API endpoints are accessible
- Test query directly: `curl http://prometheus:9090/api/v1/query`
- Review service discovery configuration

### Notification Integration Fails

**Problem**: Experiment notifications not sent

**Solutions**:
- Verify Slack/PagerDuty webhook URLs
- Check API credentials are valid
- Test webhook with curl command
- Review integration logs

## Safety Issues

### Experiment Affects Production

**Problem**: Production incident caused by chaos experiment

**Solutions**:
- Never run in production without explicit approval
- Verify blast radius is set correctly
- Test in staging environment first
- Have rollback plan ready before starting

### Rollback Triggered Unexpectedly

**Problem**: Rollback initiated when not needed

**Solutions**:
- Review threshold settings for automatic rollback
- Adjust time windows for metric evaluation
- Check for false positive alerts
- Consider manual rollback for critical systems

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
# Test experiment design without execution
python scripts/chaos_experiment.py --experiment test-01 --target api-service --failure-type pod_kill --dry-run
```

### Verbose Output

```bash
# Get detailed execution information
python scripts/chaos_experiment.py --experiment test-01 --target api-service --failure-type pod_kill --verbose
```

## Getting Help

### Script Help

```bash
# Get help for any script
python scripts/chaos_experiment.py --help
python scripts/resilience_assessment.py --help
```

### Error Messages

- Read error messages carefully
- Check logs for full stack traces
- Search error codes in documentation
- Review recent changes to environment

### Common Error Codes

- `E001`: Experiment configuration invalid
- `E002`: Target system not accessible
- `E003`: Blast radius out of range
- `E004`: Metrics collection failed
- `E005`: Rollback failed

## Prevention

### Pre-Experiment Checklist

- [ ] Run in non-production environment first
- [ ] Verify blast radius is appropriate
- [ ] Test rollback procedures
- [ ] Ensure monitoring is operational
- [ ] Notify stakeholders before experiment
- [ ] Have manual rollback plan ready
- [ ] Document expected outcomes

### During Experiment Monitoring

- Monitor metrics in real-time
- Watch for unexpected behavior
- Have kill switch ready
- Track timeline of events
- Document all observations

### Post-Experiment Actions

- Verify all metrics collected
- Validate rollback was successful
- Document lessons learned
- Update knowledge base
- Share findings with team
- Schedule follow-up experiments

## Best Practices Summary

- Start small: Begin with limited blast radius
- Test first: Always test in non-production
- Monitor closely: Watch all metrics during experiment
- Be prepared: Have rollback plan ready
- Document everything: Record hypotheses, outcomes, and learnings
- Iterate gradually: Increase complexity as confidence builds
- Include humans: Test communication and decision-making
- Learn from failures: Even failed experiments provide insights
