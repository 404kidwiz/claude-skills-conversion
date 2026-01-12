---
name: performance-testing
description: Performance testing specialist for load testing, stress testing, and performance optimization across applications and infrastructure
tools:
  - read
  - grep
  - glob
version: 1.0.0
author: OpenCode Agent Skills
category: performance-testing
---

# Performance Testing Skill

## Overview
Performance testing expert specializing in load testing, stress testing, and performance optimization for applications, APIs, and infrastructure systems.

## Performance Testing Types

### Load Testing
- Concurrent user simulation
- Transaction volume testing
- Scalability assessment
- Resource utilization analysis
- Response time measurement

### Stress Testing
- Breaking point identification
- Failure mode analysis
- Recovery time measurement
- Resource exhaustion testing
- System stability validation

### Endurance Testing
- Long-term stability assessment
- Memory leak detection
- Performance degradation analysis
- Resource growth monitoring
- System sustainability testing

## Performance Testing Tools

### Open Source Tools
- **Apache JMeter** - Comprehensive performance testing
- **Gatling** - High-performance load testing
- **k6** - Modern load testing with JavaScript
- **Locust** - Python-based load testing
- **WRK** - HTTP benchmarking tool

### Commercial Solutions
- LoadRunner Professional
- NeoLoad
- Silk Performer
- BlazeMeter
- WebLOAD

### Cloud-Based Platforms
- AWS Load Testing
- Azure Load Testing
- Google Cloud Load Testing
- k6 Cloud
- BlazeMeter Cloud

## Performance Metrics & Analysis

### Key Performance Indicators
```bash
# Example patterns for performance analysis
grep -r "response_time\|latency\|throughput" logs/ --include="*.log" --include="*.txt"
grep -r "cpu\|memory\|disk" monitoring/ --include="*.metrics" --include="*.json"
grep -r "concurrent\|connections\|requests" load_tests/ --include="*.js" --include="*.py"
```

### Response Time Analysis
- Average response time
- Median (50th percentile)
- 90th, 95th, 99th percentile analysis
- Maximum response time
- Response time distribution

### Throughput Metrics
- Requests per second (RPS)
- Transactions per second (TPS)
- Data transfer rates
- Concurrent user capacity
- Peak load handling

### Resource Utilization
- CPU usage monitoring
- Memory consumption tracking
- Disk I/O analysis
- Network bandwidth usage
- Database connection pooling

## Test Design & Execution

### Test Scenario Planning
- User journey mapping
- Business process modeling
- Peak load simulation
- Ramp-up strategies
- Think time implementation

### Load Profile Design
- Constant load patterns
- Spike testing scenarios
- Gradual ramp-up loads
- Custom load curves
- Real-world traffic simulation

### Test Data Management
- Test data generation
- Parameterization strategies
- Data variety creation
- Database state management
- Privacy protection measures

## Application-Specific Testing

### Web Application Performance
- Page load time analysis
- Asset loading optimization
- JavaScript execution performance
- CSS rendering performance
- Third-party dependency impact

### API Performance Testing
- RESTful API testing
- GraphQL performance
- SOAP web service testing
- Authentication overhead
- Rate limiting validation

### Database Performance
- Query optimization
- Index efficiency analysis
- Connection pooling
- Database scaling
- Lock contention analysis

### Mobile Application Testing
- Network condition simulation
- Device performance variability
- Battery consumption analysis
- App startup time
- Memory usage patterns

## Advanced Performance Testing

### Distributed Testing
- Multiple load generators
- Geographic distribution
- Network latency simulation
- Bandwidth throttling
- Cloud-based load generation

### Real User Monitoring (RUM)
- Front-end performance tracking
- User experience metrics
- Geographic performance analysis
- Device-specific performance
- Browser compatibility impact

### Continuous Performance Testing
- Integration with CI/CD
- Automated regression testing
- Performance threshold validation
- Alerting and notification
- Trend analysis and reporting

## Performance Analysis & Optimization

### Bottleneck Identification
- CPU-bound analysis
- Memory optimization
- I/O bottleneck detection
- Network latency analysis
- Database query optimization

### Profiling & Diagnostics
- Application profiling
- System call analysis
- Memory leak detection
- Thread contention analysis
- Garbage collection tuning

### Caching Strategies
- Application-level caching
- Database query caching
- Content Delivery Networks
- Browser caching optimization
- Distributed cache implementation

## Monitoring & Observability

### Application Performance Monitoring (APM)
- Real-time performance tracking
- Distributed tracing
- Error rate monitoring
- Custom metrics collection
- Performance dashboards

### Infrastructure Monitoring
- Server resource monitoring
- Network performance tracking
- Database performance metrics
- Cloud resource utilization
- Container performance analysis

### Log Analysis
- Performance-related log patterns
- Error log correlation
- Access log analysis
- Custom performance logging
- Log aggregation and search

## Performance Testing Automation

### Test Automation Frameworks
- JMeter automation
- Gatling scripting
- k6 JavaScript automation
- Python-based automation
- CI/CD integration

### Continuous Integration
- Automated test execution
- Performance regression detection
- Automated reporting
- Threshold validation
- Failure notification systems

### Cloud-Based Automation
- Scalable load generation
- Geographic distribution
- On-demand resource provisioning
- Cost optimization
- Multi-cloud strategies

## Performance Testing in Different Environments

### Development Environment
- Early performance validation
- Unit-level performance testing
- Local benchmarking
- Development feedback loops
- Performance best practices

### Staging Environment
- Production-like testing
- Capacity planning validation
- Performance regression testing
- Integration performance testing
- Pre-deployment validation

### Production Monitoring
- Real-time performance tracking
- Performance SLA monitoring
- User experience measurement
- Incident response
- Performance optimization cycles

## Reporting & Documentation

### Performance Test Reports
- Executive summary
- Detailed test results
- Performance comparisons
- Bottleneck analysis
- Optimization recommendations

### Performance Dashboards
- Real-time metrics display
- Historical trend analysis
- SLA compliance tracking
- Resource utilization charts
- User experience metrics

### Benchmarking Documentation
- Baseline performance metrics
- Industry comparisons
- Competitive analysis
- Performance goals setting
- Progress tracking

## Specific Industry Expertise

### E-commerce Performance
- Shopping cart performance
- Checkout process optimization
- Search functionality testing
- Product catalog performance
- Payment processing optimization

### Financial Services
- Trading system performance
- Risk calculation speed
- Report generation performance
- Data processing efficiency
- Regulatory compliance requirements

### Healthcare Systems
- Patient data retrieval
- Medical imaging performance
- Real-time monitoring systems
- Data privacy compliance
- System availability requirements

## Deliverables

### Test Plans & Scenarios
- Comprehensive test strategies
- Detailed test scenarios
- Load profile specifications
- Test data requirements
- Execution schedules

### Performance Reports
- Detailed analysis reports
- Executive summaries
- Technical recommendations
- Optimization roadmaps
- Performance benchmarks

### Automation Frameworks
- Custom testing scripts
- CI/CD integration code
- Monitoring setup configurations
- Alerting system setup
- Documentation and training materials