#!/usr/bin/env python3
"""
Error Detection Automation Script

Automates error detection and analysis by:
- Scanning logs for error patterns
- Correlating errors across services
- Detecting anomalies in error rates
- Generating error reports and alerts

Usage:
    python scripts/error_detection_automation.py --scan --services <services>
    python scripts/error_detection_automation.py --help
"""

import argparse
import json
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class LogScanner:
    """Scans logs for error patterns."""

    ERROR_PATTERNS = {
        'critical': [
            r'(?i)exception',
            r'(?i)critical',
            r'(?i)fatal',
            r'(?i)pipeline.*failed',
            r'(?i)timeout.*exceeded'
        ],
        'high': [
            r'(?i)error',
            r'(?i)failed',
            r'(?i)connection.*refused',
            r'(?i)service.*unavailable'
        ],
        'medium': [
            r'(?i)warning',
            r'(?i)deprecated',
            r'(?i)retrying',
            r'(?i)slow'
        ]
    }

    def scan_logs(self, service_name: str, log_entries: List[str]) -> Dict:
        """Scan log entries for error patterns."""
        scan_results = {
            'service': service_name,
            'scanned_at': datetime.utcnow().isoformat(),
            'total_entries': len(log_entries),
            'errors_found': {
                'critical': [],
                'high': [],
                'medium': []
            },
            'error_count_by_severity': {},
            'top_error_patterns': [],
            'error_timeline': []
        }

        for entry in log_entries:
            timestamp_str = self._extract_timestamp(entry)
            severity = self._classify_error(entry)

            if severity:
                error_info = {
                    'timestamp': timestamp_str,
                    'message': entry,
                    'severity': severity,
                    'pattern': self._match_pattern(entry)
                }

                scan_results['errors_found'][severity].append(error_info)
                scan_results['error_timeline'].append(error_info)

        # Calculate error counts
        for severity in ['critical', 'high', 'medium']:
            count = len(scan_results['errors_found'][severity])
            scan_results['error_count_by_severity'][severity] = count

        # Identify top error patterns
        scan_results['top_error_patterns'] = self._identify_top_patterns(scan_results['errors_found'])

        logger.info(f"Scanned {scan_results['total_entries']} entries, found {sum(scan_results['error_count_by_severity'].values())} errors")
        return scan_results

    def _extract_timestamp(self, log_entry: str) -> str:
        """Extract timestamp from log entry."""
        # Simple timestamp extraction (in real implementation, use proper parsing)
        timestamp_patterns = [
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',
            r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',
            r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}'
        ]

        for pattern in timestamp_patterns:
            match = re.search(pattern, log_entry)
            if match:
                return match.group(0)

        return datetime.utcnow().isoformat()

    def _classify_error(self, log_entry: str) -> str:
        """Classify error severity based on patterns."""
        for severity, patterns in self.ERROR_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, log_entry):
                    return severity
        return None

    def _match_pattern(self, log_entry: str) -> str:
        """Match error pattern in log entry."""
        for severity, patterns in self.ERROR_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, log_entry):
                    return pattern
        return None

    def _identify_top_patterns(self, errors: Dict) -> List[Dict]:
        """Identify most frequent error patterns."""
        pattern_counts = {}

        for severity in ['critical', 'high', 'medium']:
            for error in errors[severity]:
                pattern = error.get('pattern', 'unknown')
                pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

        # Sort by frequency
        sorted_patterns = sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)

        top_patterns = []
        for pattern, count in sorted_patterns[:10]:  # Top 10 patterns
            top_patterns.append({
                'pattern': pattern,
                'count': count,
                'percentage': round((count / sum(pattern_counts.values())) * 100, 2)
            })

        return top_patterns


class ErrorCorrelator:
    """Correlates errors across multiple services."""

    def correlate_errors(self, service_scans: List[Dict]) -> Dict:
        """Correlate errors across services."""
        correlation = {
            'correlation_timestamp': datetime.utcnow().isoformat(),
            'services_analyzed': len(service_scans),
            'correlated_incidents': [],
            'service_dependencies': {},
            'error_cascades': []
        }

        if len(service_scans) < 2:
            logger.info("Need at least 2 services for correlation")
            return correlation

        # Correlate errors by time windows
        time_windows = self._create_time_windows(service_scans)

        for window in time_windows:
            services_with_errors = [s for s in service_scans if self._has_errors_in_window(s, window)]

            if len(services_with_errors) >= 2:
                correlation['correlated_incidents'].append({
                    'time_window': window,
                    'affected_services': [s['service'] for s in services_with_errors],
                    'total_errors': sum(len(s['error_timeline']) for s in services_with_errors),
                    'suspected_cascade': self._detect_cascade(services_with_errors)
                })

        # Identify error cascades
        correlation['error_cascades'] = self._identify_cascades(service_scans)

        logger.info(f"Correlated {len(correlation['correlated_incidents'])} incidents across services")
        return correlation

    def _create_time_windows(self, service_scans: List[Dict]) -> List[Dict]:
        """Create time windows for correlation."""
        # Get all timestamps from all services
        all_timestamps = []
        for scan in service_scans:
            all_timestamps.extend([
                datetime.fromisoformat(e['timestamp']) for e in scan['error_timeline']
            ])

        if not all_timestamps:
            return []

        # Create 5-minute windows
        min_time = min(all_timestamps)
        max_time = max(all_timestamps)

        windows = []
        current = min_time
        while current <= max_time:
            windows.append({
                'start': current.isoformat(),
                'end': (current + timedelta(minutes=5)).isoformat()
            })
            current += timedelta(minutes=5)

        return windows

    def _has_errors_in_window(self, service_scan: Dict, window: Dict) -> bool:
        """Check if service has errors in a time window."""
        window_start = datetime.fromisoformat(window['start'])
        window_end = datetime.fromisoformat(window['end'])

        for error in service_scan['error_timeline']:
            error_time = datetime.fromisoformat(error['timestamp'])
            if window_start <= error_time <= window_end:
                return True

        return False

    def _detect_cascade(self, services_with_errors: List[Dict]) -> bool:
        """Detect if errors represent a cascade."""
        # Simple heuristic: if critical errors appear in multiple services within short time
        critical_count = sum(
            1 for s in services_with_errors
            for e in s['error_timeline']
            if e['severity'] == 'critical'
        )

        return critical_count >= 2

    def _identify_cascades(self, service_scans: List[Dict]) -> List[Dict]:
        """Identify error cascades across services."""
        cascades = []

        for i, scan1 in enumerate(service_scans):
            for scan2 in service_scans[i+1:]:
                cascade = self._find_cascade_between_services(scan1, scan2)
                if cascade:
                    cascades.append(cascade)

        return cascades

    def _find_cascade_between_services(self, scan1: Dict, scan2: Dict) -> Dict:
        """Find cascading errors between two services."""
        errors1 = [(e['timestamp'], e['severity']) for e in scan1['error_timeline']]
        errors2 = [(e['timestamp'], e['severity']) for e in scan2['error_timeline']]

        for time1, severity1 in errors1:
            for time2, severity2 in errors2:
                if severity1 in ['critical', 'high'] and severity2 in ['critical', 'high']:
                    time1_dt = datetime.fromisoformat(time1)
                    time2_dt = datetime.fromisoformat(time2)

                    # Check if errors occurred within 1 minute
                    if abs((time1_dt - time2_dt).total_seconds()) <= 60:
                        return {
                            'source_service': scan1['service'],
                            'affected_service': scan2['service'],
                            'cascade_start_time': min(time1, time2),
                            'severity': severity1,
                            'confidence': 'high'
                        }

        return None


class AnomalyDetector:
    """Detects anomalies in error rates."""

    def detect_anomalies(self, service_name: str, error_history: List[Dict]) -> Dict:
        """Detect anomalies in error rate patterns."""
        if len(error_history) < 10:
            return {'error': 'Insufficient data for anomaly detection'}

        # Calculate statistics
        error_rates = [entry.get('error_rate', 0) for entry in error_history]
        mean = sum(error_rates) / len(error_rates)
        std_dev = (sum((x - mean) ** 2 for x in error_rates) / len(error_rates)) ** 0.5

        # Detect anomalies (using 2 standard deviations as threshold)
        anomalies = []
        for entry in error_history:
            error_rate = entry.get('error_rate', 0)
            if abs(error_rate - mean) > 2 * std_dev:
                anomalies.append({
                    'timestamp': entry.get('timestamp'),
                    'error_rate': error_rate,
                    'expected_range': [mean - 2*std_dev, mean + 2*std_dev],
                    'deviation': abs(error_rate - mean),
                    'severity': 'high' if error_rate > mean + 2*std_dev else 'medium'
                })

        detection = {
            'service': service_name,
            'analyzed_at': datetime.utcnow().isoformat(),
            'statistics': {
                'mean_error_rate': round(mean, 4),
                'std_deviation': round(std_dev, 4),
                'min_error_rate': round(min(error_rates), 4),
                'max_error_rate': round(max(error_rates), 4)
            },
            'anomalies_detected': len(anomalies),
            'anomalies': anomalies,
            'baseline_established': True,
            'alert_threshold': round(mean + 2*std_dev, 4)
        }

        logger.info(f"Detected {len(anomalies)} anomalies in {service_name}")
        return detection


class ErrorReportGenerator:
    """Generates error detection reports."""

    def generate_report(self, services_scanned: List[Dict], correlation: Dict,
                      anomalies: Dict) -> Dict:
        """Generate comprehensive error detection report."""
        # Aggregate statistics
        total_errors = sum(
            sum(s.get('error_count_by_severity', {}).values())
            for s in services_scanned
        )

        critical_errors = sum(
            s.get('error_count_by_severity', {}).get('critical', 0)
            for s in services_scanned
        )

        report = {
            'report_id': f"ERROR-DET-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            'generated_at': datetime.utcnow().isoformat(),
            'summary': {
                'services_scanned': len(services_scanned),
                'total_errors': total_errors,
                'critical_errors': critical_errors,
                'correlated_incidents': len(correlation.get('correlated_incidents', [])),
                'anomalies_detected': anomalies.get('anomalies_detected', 0),
                'overall_status': 'attention_needed' if critical_errors > 0 else 'healthy'
            },
            'service_scans': services_scanned,
            'correlation_analysis': correlation,
            'anomaly_detection': anomalies,
            'recommendations': self._generate_recommendations(services_scanned, correlation, anomalies),
            'priority_actions': self._prioritize_actions(services_scanned, correlation, anomalies),
            'next_steps': [
                'Investigate critical errors',
                'Address correlated incidents',
                'Review anomaly patterns',
                'Update alerting thresholds',
                'Schedule root cause analysis'
            ]
        }

        logger.info("Error detection report generated")
        return report

    def _generate_recommendations(self, scans: List[Dict], correlation: Dict, anomalies: Dict) -> List[str]:
        """Generate recommendations based on findings."""
        recommendations = []

        # Check for critical errors
        total_critical = sum(
            s.get('error_count_by_severity', {}).get('critical', 0)
            for s in scans
        )

        if total_critical > 0:
            recommendations.append(f"Immediately investigate {total_critical} critical errors")

        # Check for correlated incidents
        if correlation.get('correlated_incidents'):
            recommendations.append(
                f"Review {len(correlation['correlated_incidents'])} correlated incidents for cascade patterns"
            )

        # Check for anomalies
        if anomalies.get('anomalies_detected', 0) > 0:
            recommendations.append(
                f"Investigate {anomalies['anomalies_detected']} anomalies for underlying issues"
            )

        # Check for recurring patterns
        for scan in scans:
            top_patterns = scan.get('top_error_patterns', [])[:3]
            for pattern in top_patterns:
                if pattern['count'] > 10:
                    recommendations.append(
                        f"Address recurring error pattern in {scan['service']}: {pattern['pattern']}"
                    )

        if not recommendations:
            recommendations.append('No critical issues detected - continue monitoring')

        return recommendations

    def _prioritize_actions(self, scans: List[Dict], correlation: Dict, anomalies: Dict) -> List[Dict]:
        """Prioritize immediate actions."""
        actions = []

        # Priority 1: Critical errors
        for scan in scans:
            critical_count = scan.get('error_count_by_severity', {}).get('critical', 0)
            if critical_count > 0:
                actions.append({
                    'priority': 'critical',
                    'action': 'Investigate critical errors',
                    'service': scan['service'],
                    'count': critical_count
                })

        # Priority 2: Cascades
        for cascade in correlation.get('error_cascades', []):
            actions.append({
                'priority': 'high',
                'action': 'Address error cascade',
                'details': f"{cascade['source_service']} → {cascade['affected_service']}"
            })

        # Priority 3: Anomalies
        if anomalies.get('anomalies_detected', 0) > 0:
            actions.append({
                'priority': 'medium',
                'action': 'Investigate anomalies',
                'count': anomalies['anomalies_detected']
            })

        return actions


def generate_sample_logs(service_name: str, error_count: int = 10) -> List[str]:
    """Generate sample log entries for testing (simulated)."""
    import random
    from datetime import datetime, timedelta

    sample_messages = [
        "[{time}] ERROR Connection refused to database server",
        "[{time}] CRITICAL Pipeline processing failed",
        "[{time}] WARNING Retrying database connection",
        "[{time}] ERROR Service unavailable: timeout exceeded",
        "[{time}] ERROR Exception in request handler",
        "[{time}] FATAL Cannot connect to upstream service",
        "[{time}] WARNING Slow response detected: 2.5s",
        "[{time}] ERROR Failed to process message",
        "[{time}] CRITICAL Out of memory error",
        "[{time}] ERROR 500 Internal Server Error"
    ]

    logs = []
    base_time = datetime.utcnow() - timedelta(hours=1)

    for i in range(error_count):
        time = base_time + timedelta(minutes=i*5)
        message = random.choice(sample_messages).replace("{time}", time.isoformat())
        logs.append(message)

    return logs


def main():
    parser = argparse.ArgumentParser(description='Automate error detection')
    parser.add_argument('--scan', action='store_true', help='Scan logs for errors')
    parser.add_argument('--services', nargs='+', help='Services to scan')
    parser.add_argument('--sample-logs', action='store_true', help='Use sample logs for testing')
    parser.add_argument('--error-count', type=int, default=20, help='Number of sample errors to generate')
    parser.add_argument('--correlate', action='store_true', help='Correlate errors across services')
    parser.add_argument('--detect-anomalies', action='store_true', help='Detect anomalies in error patterns')
    parser.add_argument('--output', help='Output file for report (JSON)')

    args = parser.parse_args()

    if not args.scan and not args.correlate and not args.detect_anomalies:
        parser.error("Please specify at least one action: --scan, --correlate, or --detect-anomalies")

    # Initialize components
    log_scanner = LogScanner()
    error_correlator = ErrorCorrelator()
    anomaly_detector = AnomalyDetector()
    reporter = ErrorReportGenerator()

    service_scans = []

    # Scan logs
    if args.scan:
        services = args.services or ['api-service', 'database-service', 'auth-service']

        for service in services:
            if args.sample_logs:
                logs = generate_sample_logs(service, args.error_count)
            else:
                # In real implementation, would read from log files
                logs = []

            if logs:
                scan = log_scanner.scan_logs(service, logs)
                service_scans.append(scan)

    # Correlate errors
    correlation = {}
    if args.correlate and len(service_scans) >= 2:
        correlation = error_correlator.correlate_errors(service_scans)

    # Detect anomalies
    anomalies = {}
    if args.detect_anomalies and service_scans:
        # Generate sample error history for anomaly detection
        for scan in service_scans:
            error_history = []
            for i in range(30):  # 30 data points
                error_history.append({
                    'timestamp': (datetime.utcnow() - timedelta(days=30-i)).isoformat(),
                    'error_rate': round(random.uniform(0.001, 0.02), 4)
                })

            anomalies[scan['service']] = anomaly_detector.detect_anomalies(scan['service'], error_history)

    # Generate report
    report = reporter.generate_report(service_scans, correlation, anomalies)

    # Output report
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        logger.info(f"Report saved to {args.output}")
    else:
        print(json.dumps(report, indent=2))

    logger.info("Error detection automation complete")


if __name__ == '__main__':
    main()
