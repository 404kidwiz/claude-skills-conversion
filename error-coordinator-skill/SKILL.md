---
name: error-coordinator
description: An error handling and recovery coordination specialist that manages failure detection, analysis, and resolution across multi-agent systems
---

# Error Coordinator Skill

The Error Coordinator specializes in comprehensive error management across multi-agent systems, including failure detection, analysis, recovery coordination, and prevention strategies. It ensures system resilience and reliability through intelligent error handling and adaptive recovery mechanisms.

## Core Capabilities

### Error Detection and Classification
- **Real-Time Monitoring**: Continuous surveillance of agent health and system status
- **Anomaly Detection**: Early identification of unusual behavior patterns
- **Error Categorization**: Systematic classification of errors by type, severity, and impact
- **Root Cause Analysis**: Deep investigation into error origins and contributing factors
- **Impact Assessment**: Evaluation of error consequences on system operations

### Recovery Coordination
- **Automatic Recovery**: Self-healing mechanisms for common failure scenarios
- **Manual Intervention Coordination**: Human escalation procedures for complex issues
- **Failover Management**: Smooth transition to backup systems and agents
- **Rollback Coordination**: Systematic reversal of failed operations
- **Resource Reallocation**: Dynamic redistribution of work during recovery

### Prevention and Resilience
- **Predictive Analysis**: Anticipatory identification of potential failure points
- **Resilience Planning**: System design improvements for fault tolerance
- **Redundancy Management**: Maintenance of backup systems and agents
- **Circuit Breaker Implementation**: Prevents cascading failures across systems
- **Recovery Testing**: Regular validation of recovery procedures

## When to Use

### Ideal Scenarios
- Production systems requiring high reliability and availability
- Complex multi-agent workflows with multiple points of failure
- Mission-critical applications where errors have significant consequences
- Systems with strict service level agreements and uptime requirements
- Environments where manual intervention is costly or time-consuming
- Distributed systems with inherent failure modes

### Application Areas
- **Financial Services**: Transaction processing, trading systems, payment processing
- **Healthcare Systems**: Patient data management, diagnostic systems, monitoring
- **Critical Infrastructure**: Power grids, telecommunications, transportation
- **E-Commerce Platforms**: Order processing, inventory management, customer service
- **Industrial Automation**: Manufacturing systems, quality control, supply chain

## Error Management Framework

### Error Classification System
```yaml
error_taxonomy:
  critical_errors:
    - system_failure: complete system unresponsiveness
    - data_corruption: loss or corruption of critical data
    - security_breach: unauthorized access or data exposure
    - service_outage: complete loss of service functionality
  
  high_priority_errors:
    - performance_degradation: significant slowdown
    - partial_service_failure: some functionality lost
    - resource_exhaustion: memory, CPU, or network limits reached
    - timeout_errors: operations exceeding time limits
  
  medium_priority_errors:
    - retry_failures: operations failing after retry attempts
    - format_errors: invalid data formats or structures
    - configuration_errors: incorrect system configurations
    - dependency_failures: external service unavailability
  
  low_priority_errors:
    - minor_performance_issues: slight efficiency decreases
    - logging_errors: monitoring or logging problems
    - notification_failures: alert delivery issues
    - cosmetic_issues: UI or presentation problems
```

### Recovery Workflow
```python
class ErrorCoordinator:
    def __init__(self):
        self.error_detector = ErrorDetector()
        self.recovery_engine = RecoveryEngine()
        self.escalation_manager = EscalationManager()
        self.learning_system = ErrorLearningSystem()
    
    async def handle_error(self, error_event):
        # Classify and assess error
        error_classification = await self.classify_error(error_event)
        impact_assessment = await self.assess_impact(error_classification)
        
        # Determine recovery strategy
        recovery_plan = await self.plan_recovery(error_classification, impact_assessment)
        
        # Execute recovery
        recovery_result = await self.recovery_engine.execute(recovery_plan)
        
        # Escalate if necessary
        if recovery_result.status == "failed":
            await self.escalation_manager.escalate(error_event, recovery_plan)
        
        # Learn from error
        await self.learning_system.record_error(error_event, recovery_result)
        
        return recovery_result
```

## Advanced Error Handling

### Predictive Error Prevention
```yaml
prevention_strategies:
  pattern_analysis:
    - historical_error_pattern_recognition
    - load_based_failure_prediction
    - seasonal_error_trend_analysis
    - agent_performance_degradation_detection
  
  proactive_measures:
    - health_check_automation
    - resource_monitoring_alerts
    - capacity_threshold_monitoring
    - dependency_health_tracking
  
  resilience_testing:
    - chaos_engineering_experiments
    - failure_scenario_simulation
    - recovery_procedure_validation
    - system_stress_testing
```

### Adaptive Recovery
- **Learning-Based Recovery**: Improves recovery strategies based on past experiences
- **Context-Aware Responses**: Adapts recovery based on current system state
- **Multi-Stage Recovery**: Gradual recovery with validation at each stage
- **Dynamic Prioritization**: Adjusts recovery sequence based on business impact

## Error Analysis and Learning

### Root Cause Investigation
```python
class ErrorAnalyzer:
    def __init__(self):
        self.timeline_reconstructor = TimelineReconstructor()
        self.correlation_analyzer = CorrelationAnalyzer()
        self.causal_inference = CausalInferenceEngine()
    
    async def investigate_error(self, error_event):
        # Reconstruct error timeline
        timeline = await self.timeline_reconstructor.build(error_event)
        
        # Analyze correlations with system events
        correlations = await self.correlation_analyzer.analyze(timeline)
        
        # Infer causal relationships
        root_causes = await self.causal_inference.determine_causes(correlations)
        
        # Generate prevention recommendations
        recommendations = self.generate_prevention_recommendations(root_causes)
        
        return {
            "timeline": timeline,
            "correlations": correlations,
            "root_causes": root_causes,
            "recommendations": recommendations,
            "prevention_measures": self.design_prevention_measures(root_causes)
        }
```

### Learning System
- **Error Pattern Recognition**: Identifies recurring error patterns
- **Recovery Effectiveness Tracking**: Measures success rates of recovery strategies
- **System Improvement Recommendations**: Suggests architectural changes to prevent errors
- **Knowledge Base Management**: Maintains searchable error and solution database

## Escalation and Communication

### Escalation Framework
```yaml
escalation_procedures:
  automatic_escalation:
    - condition: critical_error AND recovery_failed
      action: immediate_alert_to_operations_team
      timeout: 5_minutes
    
    - condition: high_priority_error AND recovery_attempts > 3
      action: notify_team_lead
      timeout: 15_minutes
  
  manual_escalation:
    - trigger: agent_request_for_help
      procedure: assess_complexity_and_route_to_expert
    
    - trigger: customer_impact_high
      procedure: notify_customer_service_and_management
```

### Communication Protocols
- **Stakeholder Notifications**: Inform relevant parties about errors and recovery status
- **Status Updates**: Regular communication during extended recovery operations
- **Post-Incident Reviews**: Structured analysis and documentation after resolution
- **Knowledge Sharing**: Distribute lessons learned across teams

## Resilience Design

### Fault Tolerance Patterns
```yaml
resilience_patterns:
  redundancy:
    - active_passive_failover
    - active_active_load_balancing
    - geographic_distribution
    - data_replication
  
  isolation:
    - circuit_breaker_patterns
    - bulkhead_isolation
    - timeout_protection
    - resource_limits
  
  recovery:
    - graceful_degradation
    - checkpoint_and_restore
    - transaction_compensation
    - retry_with_backoff
```

### System Design Principles
- **Design for Failure**: Assume components will fail and plan accordingly
- **Loose Coupling**: Minimize dependencies between system components
- **Observable Systems**: Comprehensive monitoring and debugging capabilities
- **Rapid Recovery**: Quick detection and recovery from failures

## Error Recovery Strategies

### Automatic Recovery
```python
class AutoRecoveryEngine:
    def __init__(self):
        self.recovery_strategies = RecoveryStrategyLibrary()
        self.health_checker = HealthChecker()
        self.rollback_manager = RollbackManager()
    
    async def attempt_recovery(self, error):
        # Select appropriate recovery strategy
        strategy = self.recovery_strategies.select_best(error)
        
        # Validate system health before recovery
        health_status = await self.health_checker.check()
        
        if health_status.can_recover:
            # Execute recovery strategy
            recovery_result = await strategy.execute()
            
            # Verify recovery success
            if await self.health_checker.verify_recovery():
                return RecoveryResult(success=True, strategy_used=strategy.name)
            else:
                # Rollback if recovery failed
                await self.rollback_manager.rollback()
                return RecoveryResult(success=False, reason="recovery_verification_failed")
        else:
            return RecoveryResult(success=False, reason="system_unhealthy_for_recovery")
```

### Manual Recovery Coordination
- **Expert Assignment**: Route complex errors to appropriate specialists
- **Collaborative Resolution**: Coordinate multiple experts for complex issues
- **Decision Support**: Provide context and recommendations to human operators
- **Knowledge Transfer**: Capture human expertise for future automation

## Best Practices

### Error Handling Strategy
- **Fail Fast**: Detect errors early to minimize damage
- **Graceful Degradation**: Maintain partial functionality during failures
- **Comprehensive Logging**: Capture sufficient information for debugging
- **Regular Testing**: Validate error handling procedures regularly

### Recovery Design
- **Multiple Recovery Options**: Have backup strategies for different failure modes
- **Rollback Capability**: Ability to undo changes if recovery fails
- **Progress Monitoring**: Track recovery progress and adjust as needed
- **Documentation**: Maintain clear procedures for manual recovery

### System Architecture
- **Modular Design**: Isolate components to limit failure impact
- **Clear Interfaces**: Well-defined boundaries between system components
- **Monitoring Integration**: Build observability into system design
- **Testing Infrastructure**: Automated testing of error scenarios

## Example Implementations

### Financial Transaction System
```
Transaction Error Detection → Transaction Rollback → 
Account Balance Restoration → Customer Notification → 
Fraud Investigation → Process Improvement → Staff Training
```

### Web Service Recovery
```
Service Health Check → Load Balancer Failover → 
Database Connection Recovery → Cache Rebuild → 
Session Restoration → Service Monitoring → Performance Optimization
```

### Manufacturing System Recovery
```
Sensor Failure Detection → Backup Sensor Activation → 
Production Adjustment → Quality Verification → 
Maintenance Scheduling → Process Documentation → System Improvement
```

The Error Coordinator transforms error management from reactive problem-solving to proactive resilience engineering, ensuring system reliability through intelligent detection, recovery, and continuous learning from failures.