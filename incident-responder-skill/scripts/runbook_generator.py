#!/usr/bin/env python3
"""
Runbook Generator Automation Script

Generates incident response runbooks by:
- Analyzing incident patterns
- Creating response procedures
- Including team contacts and escalation paths
- Formatting for readability and quick reference

Usage:
    python scripts/runbook_generator.py --incident-type <type> --output <file>
    python scripts/runbook_generator.py --help
"""

import argparse
import json
import logging
from datetime import datetime
from typing import Dict, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class IncidentTypeLibrary:
    """Library of incident types with standard procedures."""

    INCIDENT_TYPES = {
        'data_breach': {
            'title': 'Data Breach Response Runbook',
            'severity_default': 'critical',
            'response_time_minutes': 15,
            'phases': [
                'Immediate Containment',
                'Evidence Collection',
                'Investigation',
                'Notification',
                'Recovery',
                'Post-Incident Review'
            ]
        },
        'service_outage': {
            'title': 'Service Outage Response Runbook',
            'severity_default': 'high',
            'response_time_minutes': 10,
            'phases': [
                'Impact Assessment',
                'Diagnosis',
                'Workaround Implementation',
                'Resolution',
                'Service Restoration',
                'Post-Incident Review'
            ]
        },
        'security_violation': {
            'title': 'Security Violation Response Runbook',
            'severity_default': 'high',
            'response_time_minutes': 15,
            'phases': [
                'Identification and Classification',
                'Containment',
                'Investigation',
                'Remediation',
                'Reporting',
                'Prevention'
            ]
        },
        'database_failure': {
            'title': 'Database Failure Response Runbook',
            'severity_default': 'critical',
            'response_time_minutes': 10,
            'phases': [
                'Immediate Assessment',
                'Failover (if applicable)',
                'Diagnosis',
                'Recovery from Backup',
                'Validation',
                'Root Cause Analysis'
            ]
        },
        'network_incident': {
            'title': 'Network Incident Response Runbook',
            'severity_default': 'high',
            'response_time_minutes': 15,
            'phases': [
                'Impact Assessment',
                'Isolation',
                'Diagnosis',
                'Remediation',
                'Testing',
                'Monitoring'
            ]
        }
    }


class TeamContactsLibrary:
    """Library of team contacts and escalation paths."""

    TEAMS = {
        'incident_commander': {
            'role': 'Incident Commander',
            'primary_contact': 'on-call@company.com',
            'escalation': 'engineering-lead@company.com',
            'responsibilities': [
                'Coordinate overall response',
                'Make key decisions',
                'Communicate with stakeholders',
                'Manage timeline'
            ]
        },
        'security_engineer': {
            'role': 'Security Engineer',
            'primary_contact': 'security-oncall@company.com',
            'escalation': 'security-lead@company.com',
            'responsibilities': [
                'Security assessment',
                'Containment actions',
                'Forensics',
                'Vulnerability assessment'
            ]
        },
        'devops_engineer': {
            'role': 'DevOps Engineer',
            'primary_contact': 'devops-oncall@company.com',
            'escalation': 'devops-lead@company.com',
            'responsibilities': [
                'Infrastructure diagnosis',
                'Containment actions',
                'Recovery procedures',
                'Deployment fixes'
            ]
        },
        'backend_developer': {
            'role': 'Backend Developer',
            'primary_contact': 'backend-oncall@company.com',
            'escalation': 'backend-lead@company.com',
            'responsibilities': [
                'Application diagnosis',
                'Code fixes',
                'Testing fixes',
                'Deployment coordination'
            ]
        },
        'sre_engineer': {
            'role': 'SRE Engineer',
            'primary_contact': 'sre-oncall@company.com',
            'escalation': 'sre-lead@company.com',
            'responsibilities': [
                'Reliability assessment',
                'SLO monitoring',
                'Recovery validation',
                'Post-incident analysis'
            ]
        }
    }


class ProcedureGenerator:
    """Generates response procedures for runbooks."""

    def generate_phase_procedures(self, incident_type: str) -> List[Dict]:
        """Generate procedures for each phase of incident response."""
        incident = IncidentTypeLibrary.INCIDENT_TYPES.get(incident_type, {})
        phases = incident.get('phases', [])

        procedures = []
        for phase in phases:
            procedures.append({
                'phase': phase,
                'procedures': self._get_phase_procedures(phase),
                'estimated_time_minutes': self._get_phase_time(phase),
                'checklist': self._get_phase_checklist(phase)
            })

        return procedures

    def _get_phase_procedures(self, phase: str) -> List[str]:
        """Get procedures for a specific phase."""
        procedures_map = {
            'Immediate Containment': [
                'Isolate affected systems',
                'Revoke compromised credentials',
                'Block malicious traffic',
                'Preserve evidence'
            ],
            'Impact Assessment': [
                'Determine affected services',
                'Calculate affected user count',
                'Assess business impact',
                'Estimate revenue impact'
            ],
            'Diagnosis': [
                'Review logs and metrics',
                'Identify root cause',
                'Correlate across services',
                'Validate hypothesis'
            ],
            'Workaround Implementation': [
                'Implement temporary fix',
                'Enable circuit breakers',
                'Scale resources if needed',
                'Update status page'
            ],
            'Investigation': [
                'Collect forensic evidence',
                'Analyze attack vectors',
                'Identify data accessed',
                'Assess scope of breach'
            ],
            'Recovery': [
                'Restore from backups',
                'Apply security patches',
                'Reset credentials',
                'Validate systems'
            ],
            'Post-Incident Review': [
                'Conduct blameless postmortem',
                'Document lessons learned',
                'Update procedures',
                'Schedule follow-up actions'
            ]
        }

        return procedures_map.get(phase, ['Follow standard procedures'])

    def _get_phase_time(self, phase: str) -> int:
        """Get estimated time for a phase in minutes."""
        time_map = {
            'Immediate Containment': 15,
            'Impact Assessment': 10,
            'Diagnosis': 30,
            'Workaround Implementation': 15,
            'Investigation': 60,
            'Recovery': 60,
            'Post-Incident Review': 30
        }
        return time_map.get(phase, 15)

    def _get_phase_checklist(self, phase: str) -> List[str]:
        """Get checklist for a phase."""
        checklist_map = {
            'Immediate Containment': [
                'Systems isolated: Yes/No',
                'Credentials revoked: Yes/No',
                'Traffic blocked: Yes/No',
                'Evidence preserved: Yes/No'
            ],
            'Impact Assessment': [
                'Affected services identified: Yes/No',
                'User count calculated: Yes/No',
                'Business impact assessed: Yes/No',
                'Revenue impact estimated: Yes/No'
            ],
            'Diagnosis': [
                'Logs reviewed: Yes/No',
                'Metrics analyzed: Yes/No',
                'Root cause identified: Yes/No',
                'Hypothesis validated: Yes/No'
            ],
            'Workaround Implementation': [
                'Workaround implemented: Yes/No',
                'Circuit breakers enabled: Yes/No',
                'Resources scaled: Yes/No',
                'Status page updated: Yes/No'
            ]
        }
        return checklist_map.get(phase, [])


class CommunicationTemplates:
    """Templates for incident communication."""

    def generate_communication_plan(self, incident_type: str, severity: str) -> Dict:
        """Generate communication templates for the incident."""
        return {
            'internal_stakeholders': {
                'frequency': 'every 15 minutes (critical), every 30 minutes (high)',
                'channels': ['Slack', 'Email'],
                'template': self._get_internal_template(severity)
            },
            'customers': {
                'frequency': 'initial, every 30 minutes until resolution',
                'channels': ['Status Page', 'Email', 'Twitter'],
                'template': self._get_customer_template(severity)
            },
            'executive': {
                'frequency': 'initial, major updates, resolution',
                'channels': ['Email', 'Phone'],
                'template': self._get_executive_template(severity)
            }
        }

    def _get_internal_template(self, severity: str) -> str:
        return f"""INCIDENT UPDATE - {severity.upper()} SEVERITY

Incident ID: {{incident_id}}
Started: {{start_time}}
Status: {{status}}

Summary:
{{summary}}

Impact:
- Affected Users: {{affected_users}}
- Services Impacted: {{services}}
- Estimated Revenue Impact: {{revenue_impact}}

Next Steps:
{{next_steps}}

Contact: {{incident_commander}}
"""

    def _get_customer_template(self, severity: str) -> str:
        return f"""SERVICE UPDATE - {severity.upper()}

We are currently experiencing an issue affecting {severity.lower()} severity service.

Issue: {{issue_summary}}
Started at: {{start_time}}
Current Status: {{status}}

We are working to resolve this issue and will provide updates every 30 minutes.

Thank you for your patience.
"""

    def _get_executive_template(self, severity: str) -> str:
        return f"""EXECUTIVE INCIDENT BRIEFING

Severity: {severity.upper()}
Incident ID: {{incident_id}}
Started: {{start_time}}

Executive Summary:
{{executive_summary}}

Business Impact:
- Affected Users: {{affected_users}} ({{percentage}}%)
- Revenue Impact: ${{revenue_impact}}
- SLA Breach: {{sla_breach}}

Current Status: {{status}}
Actions Taken:
{{actions}}

Next Steps:
{{next_steps}}

Timeline: {{timeline}}
"""


class RunbookGenerator:
    """Main runbook generator class."""

    def __init__(self):
        self.procedure_generator = ProcedureGenerator()
        self.communication_templates = CommunicationTemplates()

    def generate_runbook(self, incident_type: str, custom_title: str = None) -> Dict:
        """Generate complete runbook for an incident type."""
        incident = IncidentTypeLibrary.INCIDENT_TYPES.get(incident_type, {})

        if not incident:
            logger.error(f"Unknown incident type: {incident_type}")
            return None

        title = custom_title or incident.get('title')
        logger.info(f"Generating runbook: {title}")

        runbook = {
            'title': title,
            'incident_type': incident_type,
            'generated_at': datetime.utcnow().isoformat(),
            'metadata': {
                'default_severity': incident.get('severity_default'),
                'target_response_time_minutes': incident.get('response_time_minutes'),
                'last_updated': datetime.utcnow().isoformat()
            },
            'response_phases': self.procedure_generator.generate_phase_procedures(incident_type),
            'team_contacts': TeamContactsLibrary.TEAMS,
            'communication_plan': self.communication_templates.generate_communication_plan(
                incident_type, incident.get('severity_default')
            ),
            'escalation_matrix': {
                'tier_1': 'On-call team',
                'tier_2': 'Team lead',
                'tier_3': 'Engineering management',
                'tier_4': 'VP Engineering'
            },
            'tools_and_resources': [
                'Slack for coordination',
                'PagerDuty for alerting',
                'Jira for tracking',
                'Confluence for documentation',
                'Status page for external communication'
            ],
            'checklist_summary': self._generate_summary_checklist(incident.get('phases', []))
        }

        logger.info("Runbook generated successfully")
        return runbook

    def _generate_summary_checklist(self, phases: List[str]) -> Dict:
        """Generate summary checklist for the runbook."""
        return {
            'pre_incident': [
                'Ensure on-call coverage',
                'Verify alerting is operational',
                'Test communication channels',
                'Review recent runbooks'
            ],
            'during_incident': [
                'Activate Incident Commander',
                'Track all actions',
                'Communicate regularly',
                'Document decisions',
                'Preserve evidence'
            ],
            'post_incident': [
                'Complete postmortem',
                'Document lessons learned',
                'Update runbooks',
                'Schedule improvements',
                'Train teams'
            ]
        }


def generate_markdown(runbook: Dict) -> str:
    """Convert runbook dictionary to markdown format."""
    lines = []
    lines.append(f"# {runbook['title']}\n")
    lines.append(f"**Generated:** {runbook['generated_at']}\n")
    lines.append(f"**Incident Type:** {runbook['incident_type']}\n")

    # Metadata
    lines.append("## Metadata\n")
    lines.append(f"- **Default Severity:** {runbook['metadata']['default_severity']}")
    lines.append(f"- **Target Response Time:** {runbook['metadata']['target_response_time_minutes']} minutes\n")

    # Response Phases
    lines.append("## Response Phases\n")
    for phase in runbook['response_phases']:
        lines.append(f"### {phase['phase']}")
        lines.append(f"**Estimated Time:** {phase['estimated_time_minutes']} minutes\n")
        lines.append("**Procedures:**")
        for proc in phase['procedures']:
            lines.append(f"- {proc}")
        lines.append("\n**Checklist:**")
        for item in phase['checklist']:
            lines.append(f"- [ ] {item}")
        lines.append("")

    # Team Contacts
    lines.append("## Team Contacts\n")
    for team_name, team_info in runbook['team_contacts'].items():
        lines.append(f"### {team_info['role']}")
        lines.append(f"- **Primary Contact:** {team_info['primary_contact']}")
        lines.append(f"- **Escalation:** {team_info['escalation']}")
        lines.append("- **Responsibilities:**")
        for resp in team_info['responsibilities']:
            lines.append(f"  - {resp}")
        lines.append("")

    # Communication Plan
    lines.append("## Communication Plan\n")
    for audience, plan in runbook['communication_plan'].items():
        lines.append(f"### {audience.replace('_', ' ').title()}")
        lines.append(f"- **Frequency:** {plan['frequency']}")
        lines.append(f"- **Channels:** {', '.join(plan['channels'])}")
        lines.append("")

    # Tools and Resources
    lines.append("## Tools and Resources\n")
    for tool in runbook['tools_and_resources']:
        lines.append(f"- {tool}")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description='Generate incident response runbook')
    parser.add_argument('--incident-type', choices=list(IncidentTypeLibrary.INCIDENT_TYPES.keys()),
                      required=True, help='Type of incident')
    parser.add_argument('--title', help='Custom title for runbook')
    parser.add_argument('--output', help='Output file for runbook (JSON)')
    parser.add_argument('--markdown', help='Output file for markdown version')
    parser.add_argument('--format', choices=['json', 'markdown', 'both'], default='json',
                      help='Output format')

    args = parser.parse_args()

    # Generate runbook
    generator = RunbookGenerator()
    runbook = generator.generate_runbook(args.incident_type, args.title)

    if not runbook:
        logger.error("Failed to generate runbook")
        return

    # Output based on format
    if args.format in ['json', 'both']:
        output_file = args.output or f"{args.incident_type}_runbook.json"
        with open(output_file, 'w') as f:
            json.dump(runbook, f, indent=2)
        logger.info(f"JSON runbook saved to {output_file}")

    if args.format in ['markdown', 'both']:
        markdown_file = args.markdown or f"{args.incident_type}_runbook.md"
        markdown_content = generate_markdown(runbook)
        with open(markdown_file, 'w') as f:
            f.write(markdown_content)
        logger.info(f"Markdown runbook saved to {markdown_file}")


if __name__ == '__main__':
    main()
