"""
Incident Classification and Triage
Automated incident response system
"""

import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
from pathlib import Path

try:
    import requests
except ImportError:
    raise ImportError("requests required: pip install requests")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class IncidentType(Enum):
    SERVICE_DOWN = "service_down"
    PERFORMANCE = "performance"
    DATA_LOSS = "data_loss"
    SECURITY = "security"
    INFRASTRUCTURE = "infrastructure"
    APPLICATION = "application"
    NETWORK = "network"


@dataclass
class Incident:
    id: str
    title: str
    description: str
    severity: Severity
    incident_type: IncidentType
    source: str
    timestamp: datetime
    affected_services: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    assigned_to: Optional[str] = None
    status: str = "new"
    acknowledged: bool = False
    resolved: bool = False
    resolution_notes: Optional[str] = None


@dataclass
class OnCallSchedule:
    primary: str
    secondary: str
    rotation_start: datetime
    rotation_end: datetime


class IncidentTriageSystem:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.incidents: List[Incident] = []
        self.on_call_schedule: Optional[OnCallSchedule] = None
        self.notification_channels = []

    def classify_incident(
        self,
        title: str,
        description: str,
        metrics: Optional[Dict[str, Any]] = None,
        source: str = "monitoring"
    ) -> Incident:
        logger.info(f"Classifying incident: {title}")

        severity = self._classify_severity(title, description, metrics)
        incident_type = self._classify_incident_type(title, description)
        affected_services = self._extract_affected_services(title, description)

        incident = Incident(
            id=self._generate_incident_id(),
            title=title,
            description=description,
            severity=severity,
            incident_type=incident_type,
            source=source,
            timestamp=datetime.utcnow(),
            affected_services=affected_services,
            metadata=metrics or {}
        )

        return incident

    def _classify_severity(
        self,
        title: str,
        description: str,
        metrics: Optional[Dict[str, Any]]
    ) -> Severity:
        title_lower = title.lower()
        description_lower = description.lower()

        # Critical indicators
        critical_keywords = [
            'down', 'outage', 'crash', 'failure', 'critical',
            'emergency', 'data loss', 'security breach'
        ]

        for keyword in critical_keywords:
            if keyword in title_lower or keyword in description_lower:
                return Severity.CRITICAL

        # High indicators
        high_keywords = ['degraded', 'slow', 'latency', 'timeout', 'error rate']

        for keyword in high_keywords:
            if keyword in title_lower or keyword in description_lower:
                return Severity.HIGH

        # Metric-based classification
        if metrics:
            error_rate = metrics.get('error_rate', 0)
            latency_p99 = metrics.get('latency_p99', 0)

            if error_rate > 0.1:  # >10% error rate
                return Severity.CRITICAL
            elif error_rate > 0.05:  # >5% error rate
                return Severity.HIGH
            elif latency_p99 > 5000:  # >5s latency
                return Severity.HIGH
            elif latency_p99 > 1000:  # >1s latency
                return Severity.MEDIUM

        return Severity.LOW

    def _classify_incident_type(
        self,
        title: str,
        description: str
    ) -> IncidentType:
        text = f"{title} {description}".lower()

        type_keywords = {
            IncidentType.SERVICE_DOWN: ['down', 'outage', 'unavailable', 'crash'],
            IncidentType.PERFORMANCE: ['slow', 'latency', 'timeout', 'performance'],
            IncidentType.DATA_LOSS: ['data loss', 'corruption', 'missing data'],
            IncidentType.SECURITY: ['security', 'breach', 'attack', 'unauthorized'],
            IncidentType.INFRASTRUCTURE: ['server', 'database', 'infrastructure', 'hardware'],
            IncidentType.APPLICATION: ['application', 'app', 'software', 'bug'],
            IncidentType.NETWORK: ['network', 'connectivity', 'dns', 'firewall']
        }

        for incident_type, keywords in type_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return incident_type

        return IncidentType.APPLICATION

    def _extract_affected_services(
        self,
        title: str,
        description: str
    ) -> List[str]:
        text = f"{title} {description}".lower()

        known_services = [
            'api', 'database', 'web', 'auth', 'payment',
            'email', 'cdn', 'cache', 'queue', 'worker'
        ]

        affected = [service for service in known_services if service in text]
        return affected

    def _generate_incident_id(self) -> str:
        return f"INC-{datetime.now().strftime('%Y%m%d%H%M%S')}-{len(self.incidents):04d}"

    def triage_incident(self, incident: Incident) -> Dict[str, Any]:
        logger.info(f"Triage for incident {incident.id}")

        triage_result = {
            'incident_id': incident.id,
            'severity': incident.severity.value,
            'type': incident.incident_type.value,
            'actions': [],
            'estimated_resolution_time': None
        }

        # Determine actions based on severity
        if incident.severity == Severity.CRITICAL:
            triage_result['actions'].append('Page on-call engineer immediately')
            triage_result['actions'].append('Engage incident commander')
            triage_result['actions'].append('Create war room')
            triage_result['estimated_resolution_time'] = 30  # minutes

        elif incident.severity == Severity.HIGH:
            triage_result['actions'].append('Page on-call engineer')
            triage_result['actions'].append('Notify team lead')
            triage_result['estimated_resolution_time'] = 60

        elif incident.severity == Severity.MEDIUM:
            triage_result['actions'].append('Notify on-call via Slack')
            triage_result['actions'].append('Create ticket')
            triage_result['estimated_resolution_time'] = 120

        else:
            triage_result['actions'].append('Create ticket for next business day')
            triage_result['estimated_resolution_time'] = None

        return triage_result

    def notify_stakeholders(
        self,
        incident: Incident,
        channels: Optional[List[str]] = None
    ):
        if channels is None:
            channels = ['email', 'slack']

        logger.info(f"Notifying stakeholders for incident {incident.id}")

        notification_data = {
            'incident_id': incident.id,
            'title': incident.title,
            'severity': incident.severity.value,
            'type': incident.incident_type.value,
            'affected_services': incident.affected_services,
            'description': incident.description,
            'timestamp': incident.timestamp.isoformat()
        }

        for channel in channels:
            self._send_notification(channel, notification_data)

    def _send_notification(self, channel: str, data: Dict[str, Any]):
        if channel == 'slack':
            self._send_slack_notification(data)
        elif channel == 'email':
            self._send_email_notification(data)
        elif channel == 'pagerduty':
            self._send_pagerduty_notification(data)
        else:
            logger.warning(f"Unknown notification channel: {channel}")

    def _send_slack_notification(self, data: Dict[str, Any]):
        webhook_url = self.config.get('slack_webhook_url')

        if not webhook_url:
            logger.info("Slack webhook not configured, skipping notification")
            return

        message = {
            'text': f"Incident Alert: {data['title']}",
            'blocks': [
                {
                    'type': 'header',
                    'text': {
                        'type': 'plain_text',
                        'text': f"Incident {data['incident_id']}: {data['title']}"
                    }
                },
                {
                    'type': 'section',
                    'fields': [
                        {
                            'type': 'mrkdwn',
                            'text': f"*Severity:*\n{data['severity'].upper()}"
                        },
                        {
                            'type': 'mrkdwn',
                            'text': f"*Type:*\n{data['type']}"
                        }
                    ]
                },
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': f"*Description:*\n{data['description']}"
                    }
                }
            ]
        }

        try:
            response = requests.post(webhook_url, json=message)
            response.raise_for_status()
            logger.info("Slack notification sent")
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")

    def _send_email_notification(self, data: Dict[str, Any]):
        logger.info(f"Email notification would be sent for incident {data['incident_id']}")
        # Implementation would use SMTP library

    def _send_pagerduty_notification(self, data: Dict[str, Any]):
        api_key = self.config.get('pagerduty_api_key')

        if not api_key:
            logger.info("PagerDuty not configured, skipping notification")
            return

        if data['severity'] in ['critical', 'high']:
            try:
                # Implementation would call PagerDuty API
                logger.info("PagerDuty alert triggered")
            except Exception as e:
                logger.error(f"Failed to send PagerDuty notification: {e}")

    def create_incident_ticket(self, incident: Incident) -> str:
        logger.info(f"Creating ticket for incident {incident.id}")

        # Implementation would integrate with Jira, ServiceNow, etc.
        ticket_id = f"TKT-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        logger.info(f"Ticket created: {ticket_id}")
        return ticket_id

    def acknowledge_incident(self, incident_id: str, acknowledged_by: str):
        for incident in self.incidents:
            if incident.id == incident_id:
                incident.acknowledged = True
                incident.assigned_to = acknowledged_by
                incident.status = "acknowledged"
                logger.info(f"Incident {incident_id} acknowledged by {acknowledged_by}")
                return

        logger.warning(f"Incident {incident_id} not found")

    def resolve_incident(
        self,
        incident_id: str,
        resolution_notes: str,
        resolved_by: str
    ):
        for incident in self.incidents:
            if incident.id == incident_id:
                incident.resolved = True
                incident.resolution_notes = resolution_notes
                incident.status = "resolved"
                incident.assigned_to = resolved_by
                logger.info(f"Incident {incident_id} resolved by {resolved_by}")

                # Notify resolution
                self.notify_resolution(incident)
                return

        logger.warning(f"Incident {incident_id} not found")

    def notify_resolution(self, incident: Incident):
        logger.info(f"Notifying resolution for incident {incident.id}")
        # Implementation would send resolution notifications


def main():
    system = IncidentTriageSystem()

    # Example incident
    incident = system.classify_incident(
        title="API service down",
        description="The main API is returning 500 errors for all endpoints",
        metrics={'error_rate': 1.0, 'latency_p99': 0},
        source="monitoring"
    )

    triage_result = system.triage_incident(incident)
    print(f"Triage result: {json.dumps(triage_result, indent=2)}")

    # Notify
    system.notify_stakeholders(incident, channels=['slack'])

    # Create ticket
    ticket_id = system.create_incident_ticket(incident)
    print(f"Created ticket: {ticket_id}")


if __name__ == "__main__":
    main()
