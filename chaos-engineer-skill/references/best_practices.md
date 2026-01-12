# Chaos Engineer - Best Practices

This guide outlines best practices for chaos engineering, controlled failure injection, and building resilient systems.

## Core Principles

### Hypothesis-Driven Experiments

- Always start with a clear hypothesis
- Define steady state metrics before experimenting
- Set success criteria upfront
- Validate or invalidate hypothesis based on data

**Example Hypothesis**:
"The system api-service remains available (error rate < 1%) when 20% of pods are killed"

### Controlled Blast Radius

- **Development**: 100% blast radius acceptable
- **Staging**: 50-100% blast radius
- **Production**: 1-10% blast radius maximum
- **Canary**: Start with 1%, increase gradually

### Automated Rollback

- **Target**: Rollback within 30 seconds if needed
- **Method**: Automated kill switch or circuit breaker
- **Monitoring**: Real-time monitoring of key metrics
- **Validation**: Verify system health after rollback

## Experiment Design Best Practices

### Define Clear Hypotheses

Use SMART hypotheses:
- **S**pecific: Clear statement about expected behavior
- **M**easurable: Can be validated with metrics
- **A**chievable: Within system capabilities
- **R**ealistic: Based on understanding of system
- **T**ime-bound: Clear time window for validation

**Good Hypothesis**:
"System remains available (error rate < 0.5%, latency p95 < 500ms) when network latency of 200ms is injected for 5 minutes"

**Bad Hypothesis**:
"System works fine when we break things"

### Identify Steady State Metrics

Track these metrics before, during, and after experiments:
- **Error Rate**: Percentage of failed requests
- **Latency**: p50, p95, p99 response times
- **Throughput**: Requests per second
- **Availability**: Uptime percentage
- **Resource Usage**: CPU, memory, disk, network

### Plan Safety Mechanisms

- Automated kill switches
- Manual emergency stop buttons
- Circuit breakers for protection
- Alert thresholds for auto-rollback
- Communication channels for coordination

## Failure Injection Best Practices

### Start Simple

1. **Pod Kill**: Easiest failure to inject and recover from
2. **Network Latency**: Introduce controlled delay
3. **Packet Loss**: Test resilience to data loss
4. **Memory Stress**: Simulate memory exhaustion
5. **Complex Scenarios**: Combine multiple failures

### Progressive Complexity

- **Week 1**: Single failure types in development
- **Week 2**: Multiple failures in staging
- **Week 3**: Combined failures with smaller blast radius in production
- **Week 4**: Game days with complex scenarios

### Target Critical Paths

- Test customer-facing services first
- Include downstream dependencies
- Test authentication and authorization flows
- Include database and storage systems
- Test network and infrastructure components

## Blast Radius Control

### Traffic Percentage

Use these blast radius percentages:
- **Development**: 100%
- **Staging**: 50-100%
- **Production Canary**: 1-5%
- **Production Standard**: 5-10%

### User Segmentation

- **Internal Users**: Test with internal traffic first
- **Beta Customers**: Test with selected customer segment
- **Geographic**: Limit to specific regions
- **Feature Flags**: Use feature flags to isolate experiments

### Environment Isolation

- Use dedicated namespaces for chaos experiments
- Separate monitoring for experiment tracking
- Isolate resources to prevent cross-contamination
- Clean up all experiment resources after completion

## Monitoring During Experiments

### Real-Time Dashboards

Create dashboards showing:
- Error rate by service
- Latency distribution
- Throughput over time
- System resource utilization
- Active experiment status

### Alert Thresholds

Set alerts for:
- Error rate > 1% for > 1 minute
- Latency p95 > 1000ms
- Available instances < 50%
- CPU > 80% for > 2 minutes
- Automatic rollback trigger

### Observability

- Collect logs from all services
- Trace requests across service boundaries
- Monitor system events and metrics
- Track experiment timeline in central system

## Game Day Planning

### Pre-Game Day Preparation

- Choose realistic scenarios based on incidents
- Prepare runbooks and procedures
- Set up communication channels
- Assign roles: Incident Commander, Scribe, Observers
- Schedule during low-traffic periods
- Have rollback plan documented

### During Game Day

- Activate Incident Commander
- Follow runbook procedures
- Document all actions and decisions
- Monitor metrics continuously
- Communicate updates regularly
- Time all procedures

### Post-Game Day

- Conduct blameless postmortem
- Document what went well
- Identify areas for improvement
- Update runbooks based on findings
- Share lessons with wider team
- Schedule follow-up game day

## Continuous Chaos

### Automated Experiments

- Schedule experiments in CI/CD pipeline
- Run experiments on every deployment
- Test new features with chaos
- Automate analysis of results
- Generate experiment reports automatically

### Integration with Development

- Include chaos tests in PR checks
- Block deployments if experiment fails
- Require chaos testing for critical services
- Integrate with existing monitoring
- Use experiment results for capacity planning

### Knowledge Management

- Maintain catalog of all experiments
- Tag experiments by service and failure type
- Track hypotheses and outcomes
- Store experiment reports for reference
- Update patterns and best practices

## Safety Guidelines

### Production Experiments

- Never experiment in production without approval
- Get explicit sign-off from engineering lead
- Schedule maintenance windows if needed
- Use smallest possible blast radius
- Have on-call team on standby
- Test rollback procedure before experiment

### Emergency Procedures

- Kill switch: Stop experiment immediately if critical
- Rollback: Execute rollback within 30 seconds
- Communication: Notify all stakeholders immediately
- Escalation: Elevate to management if impact severe
- Documentation: Record all actions taken

### Risk Assessment

Before each experiment:
- Assess potential customer impact
- Identify critical business functions at risk
- Estimate financial impact if things go wrong
- Prepare mitigation strategies
- Verify rollback procedures work

## Building Resilience

### Patterns to Implement

#### Circuit Breaker
- Opens when failure threshold reached
- Prevents cascading failures
- Supports automatic recovery
- Include fallback mechanisms

#### Retry with Backoff
- Retry transient failures
- Use exponential backoff
- Set maximum retry limit
- Implement jitter for distributed systems

#### Bulkhead
- Isolate resource pools
- Prevent resource exhaustion
- Maintain partial service during failures
- Queue requests when resources full

#### Timeout Configuration
- Set appropriate timeouts for all operations
- Fail fast instead of hanging
- Include timeout in monitoring
- Document timeout expectations

#### Fallback Mechanisms
- Provide alternative services
- Gracefully degrade functionality
- Return cached responses when available
- Maintain core service during outages

### Monitoring Resilience

#### Single Points of Failure

- Regularly audit infrastructure for SPOFs
- Test failover for all critical systems
- Implement redundancy where missing
- Document SPOFs and mitigation plans

#### Health Checks

- Implement liveness and readiness probes
- Test all dependencies
- Use health check results for routing
- Alert on health check failures

#### Capacity Planning

- Monitor resource utilization
- Plan for peak load
- Implement auto-scaling
- Test system at maximum capacity

## Metrics and KPIs

### Chaos Engineering Metrics

- **Experiments Run**: Target 40-60 per quarter
- **Failures Discovered**: Track critical issues found
- **MTTR Improvement**: Measure reduction in recovery time
- **Blast Radius Compliance**: Track production blast radius stays <10%
- **Rollback Time**: Track rollback performance (target <30s)
- **Customer Impact**: Zero customer-facing incidents from chaos

### System Resilience Metrics

- **Availability**: Target 99.9% or higher
- **MTTR**: Target <60 minutes for high severity incidents
- **Mean Time Between Failures (MTBF)**: Track improvement over time
- **Error Rate**: Target <0.1% under normal operation
- **Recovery Time**: Measure time to return to steady state

## Team Coordination

### Roles

- **Chaos Engineer**: Design and execute experiments
- **SRE Engineer**: Define steady state and monitor metrics
- **Service Owner**: Approve experiments in production
- **On-call Team**: Execute rollback if needed
- **Stakeholder**: Review results and approve improvements

### Communication

- Notify stakeholders before production experiments
- Share experiment schedules with on-call teams
- Provide clear timelines and expected impact
- Share results and learnings widely
- Document all experiments for team knowledge

## Learning from Failures

### Post-Experiment Analysis

- Validate or invalidate hypothesis
- Document what happened and why
- Identify unexpected behaviors
- Capture system responses
- Note areas for improvement

### Continuous Improvement

- Update runbooks based on findings
- Implement discovered fixes
- Add new test cases based on issues found
- Share learnings across teams
- Repeat experiments after improvements

## Tooling

### Recommended Tools

- **Chaos Mesh**: Kubernetes-native chaos engineering
- **LitmusChaos**: Cloud-native chaos tooling
- **Gremlin**: SaaS chaos engineering platform
- **Chaos Monkey**: Netflix's chaos tool
- **Pumba**: Docker-based chaos tooling

### Integration

- Integrate with existing monitoring (Prometheus, Datadog)
- Connect to alerting systems (PagerDuty)
- Use CI/CD for automated experiments
- Store results in knowledge base
- Generate reports for team review
