#!/usr/bin/env python3
"""
Incident Triage Automation Script

Automates initial incident triage by:
- Classifying incident severity based on impact
- Routing to appropriate response teams
- Collecting initial metrics and evidence
- Generating initial triage report

Usage:
    python scripts/incident_triage.py --incident <incident_id> --description <text>
    python scripts/incident_triage.py --help
"""

import argparse
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class IncidentSeverity:
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IncidentClassifier:
    """Classifies incidents based on impact and urgency."""

    IMPACT_WEIGHTS = {
        'data_breach': 5,
        'service_outage': 4,
        'service_degradation': 3,
        'security_violation': 4,
        'compliance_issue': 3,
        'user_complaints': 2,
        'internal_error': 1
    }

    URGENCY_WEIGHTS = {
        'immediate': 3,
        'within_hours': 2,
        'within_day': 1,
        'within_week': 0.5
    }

    def classify(self, impact_type: str, urgency: str, affected_users: int) -> str:
        """Determine incident severity level."""
        impact_score = self.IMPACT_WEIGHTS.get(impact_type, 1)
        urgency_score = self.URGENCY_WEIGHTS.get(urgency, 1)
        user_multiplier = min(affected_users / 1000, 2)

        total_score = impact_score * urgency_score * user_multiplier

        if total_score >= 15:
            return IncidentSeverity.CRITICAL
        elif total_score >= 8:
            return IncidentSeverity.HIGH
        elif total_score >= 4:
            return IncidentSeverity.MEDIUM
        else:
            return IncidentSeverity.LOW


class TeamRouter:
    """Routes incidents to appropriate response teams."""

    TEAM_MAPPING = {
        'critical': ['security-engineer', 'devops-incident-responder', 'sre-engineer'],
        'high': ['devops-incident-responder', 'security-engineer', 'backend-developer'],
        'medium': ['devops-incident-responder', 'backend-developer'],
        'low': ['backend-developer', 'qa-expert']
    }

    def route(self, severity: str, incident_type: str) -> List[str]:
        """Determine which teams should respond."""
        teams = self.TEAM_MAPPING.get(severity, ['backend-developer'])

        # Add type-specific teams
        if 'security' in incident_type.lower():
            teams.insert(0, 'security-engineer')
        elif 'database' in incident_type.lower():
            teams.insert(0, 'database-administrator')
        elif 'network' in incident_type.lower():
            teams.insert(0, 'network-engineer')

        return list(dict.fromkeys(teams))  # Remove duplicates while preserving order


class EvidenceCollector:
    """Collects initial evidence for incident investigation."""

    def collect_metrics(self, service_name: str) -> Dict:
        """Collect initial service metrics."""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'service': service_name,
            'metrics': {
                'error_rate': 0.0,
                'latency_p95': 0,
                'requests_per_second': 0,
                'affected_users': 0
            },
            'status': 'initial_triage'
        }

    def collect_logs(self, service_name: str, time_window_minutes: int = 30) -> Dict:
        """Collect recent log entries."""
        return {
            'service': service_name,
            'time_window': f'{time_window_minutes}m',
            'log_count': 0,
            'error_count': 0,
            'warning_count': 0,
            'status': 'collection_initiated'
        }


class TriageReportGenerator:
    """Generates triage reports."""

    def generate_report(self, incident_id: str, classification: Dict, teams: List[str],
                    metrics: Dict, evidence: Dict) -> Dict:
        """Generate comprehensive triage report."""
        return {
            'incident_id': incident_id,
            'triage_timestamp': datetime.utcnow().isoformat(),
            'severity': classification.get('severity'),
            'impact_score': classification.get('score'),
            'assigned_teams': teams,
            'initial_metrics': metrics,
            'collected_evidence': evidence,
            'recommended_actions': self._get_recommended_actions(classification.get('severity')),
            'next_steps': [
                'Notify assigned teams',
                'Begin investigation',
                'Implement temporary mitigation if needed',
                'Update stakeholders'
            ]
        }

    def _get_recommended_actions(self, severity: str) -> List[str]:
        """Get severity-specific recommended actions."""
        actions = {
            'critical': [
                'Activate incident commander',
                'Enable all communication channels',
                'Begin immediate containment',
                'Prepare public communication'
            ],
            'high': [
                'Assign primary responder',
                'Begin detailed investigation',
                'Prepare mitigation plan',
                'Update all stakeholders'
            ],
            'medium': [
                'Assign to appropriate team',
                'Begin standard investigation',
                'Monitor for escalation',
                'Schedule follow-up'
            ],
            'low': [
                'Add to team backlog',
                'Prioritize based on impact',
                'Standard investigation process',
                'Document findings'
            ]
        }
        return actions.get(severity, actions['low'])


def main():
    parser = argparse.ArgumentParser(description='Automate incident triage')
    parser.add_argument('--incident', required=True, help='Incident ID')
    parser.add_argument('--description', required=True, help='Incident description')
    parser.add_argument('--impact', choices=['data_breach', 'service_outage', 'service_degradation',
                                            'security_violation', 'compliance_issue', 'user_complaints', 'internal_error'],
                      default='service_outage', help='Type of impact')
    parser.add_argument('--urgency', choices=['immediate', 'within_hours', 'within_day', 'within_week'],
                      default='immediate', help='Required response time')
    parser.add_argument('--affected-users', type=int, default=0,
                      help='Number of affected users')
    parser.add_argument('--service', help='Affected service name')
    parser.add_argument('--output', help='Output file for triage report (JSON)')

    args = parser.parse_args()

    # Initialize components
    classifier = IncidentClassifier()
    router = TeamRouter()
    collector = EvidenceCollector()
    reporter = TriageReportGenerator()

    logger.info(f"Starting triage for incident {args.incident}")

    # Classify incident
    severity = classifier.classify(args.impact, args.urgency, args.affected_users)
    classification = {
        'severity': severity,
        'impact_type': args.impact,
        'urgency': args.urgency,
        'affected_users': args.affected_users,
        'score': classifier.IMPACT_WEIGHTS.get(args.impact, 1) *
                  classifier.URGENCY_WEIGHTS.get(args.urgency, 1) *
                  min(args.affected_users / 1000, 2)
    }

    logger.info(f"Incident classified as {severity.upper()} severity")

    # Route to teams
    teams = router.route(severity, args.description)
    logger.info(f"Incident routed to teams: {', '.join(teams)}")

    # Collect initial evidence
    service_name = args.service or 'unknown_service'
    metrics = collector.collect_metrics(service_name)
    logs = collector.collect_logs(service_name)
    evidence = {'metrics': metrics, 'logs': logs}

    logger.info("Initial evidence collection initiated")

    # Generate report
    report = reporter.generate_report(args.incident, classification, teams, metrics, logs)
    logger.info("Triage report generated")

    # Output report
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        logger.info(f"Report saved to {args.output}")
    else:
        print(json.dumps(report, indent=2))

    logger.info("Triage complete")


if __name__ == '__main__':
    main()
