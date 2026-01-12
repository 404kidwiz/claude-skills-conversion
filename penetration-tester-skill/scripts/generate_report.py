#!/usr/bin/env python3
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
import argparse
import yaml
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ReportGenerator:
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.findings = []
        self.metadata = {}

    def _load_config(self, config_path: Optional[str]) -> Dict:
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        return {
            'report_format': 'markdown',
            'include_cvss': True,
            'include_poc': True,
            'client_name': 'Client',
            'tester_name': 'Security Team'
        }

    def calculate_cvss_score(self, finding: Dict) -> float:
        base_score = finding.get('severity_score', 0)
        
        exploitability = finding.get('exploitability', 'Medium')
        impact = finding.get('impact', 'Medium')
        
        multiplier = 1.0
        if exploitability == 'High' and impact == 'High':
            multiplier = 1.2
        elif exploitability == 'Low' and impact == 'Low':
            multiplier = 0.8
        
        return round(base_score * multiplier, 1)

    def load_findings(self, findings_file: str):
        try:
            with open(findings_file, 'r') as f:
                self.findings = json.load(f)
            logger.info(f"Loaded {len(self.findings)} findings from {findings_file}")
        except Exception as e:
            logger.error(f"Error loading findings: {str(e)}")

    def generate_executive_summary(self) -> str:
        summary = {
            'critical': len([f for f in self.findings if f.get('severity') == 'critical']),
            'high': len([f for f in self.findings if f.get('severity') == 'high']),
            'medium': len([f for f in self.findings if f.get('severity') == 'medium']),
            'low': len([f for f in self.findings if f.get('severity') == 'low'])
        }
        
        total = sum(summary.values())
        risk_level = 'Low'
        if summary['critical'] > 0 or summary['high'] > 2:
            risk_level = 'High'
        elif summary['high'] > 0 or summary['medium'] > 5:
            risk_level = 'Medium'
        
        return f"""
# Executive Summary

**Report Date:** {datetime.now().strftime('%B %d, %Y')}
**Client:** {self.config.get('client_name', 'Client')}
**Tester:** {self.config.get('tester_name', 'Security Team')}

## Overall Risk Assessment
**Risk Level:** {risk_level}
**Total Vulnerabilities:** {total}

## Vulnerability Breakdown

| Severity | Count | Risk Level |
|----------|-------|------------|
| Critical | {summary['critical']} | Immediate Action Required |
| High     | {summary['high']} | Urgent Action Required |
| Medium   | {summary['medium']} | Action Required |
| Low      | {summary['low']} | Monitor |

## Key Findings

{self._generate_key_findings()}

## Recommendations

1. **Immediate Actions (24-48 hours)**
   - Remediate all critical vulnerabilities
   - Implement temporary mitigations
   - Notify stakeholders

2. **Short-term Actions (1-2 weeks)**
   - Address all high severity issues
   - Update security controls
   - Conduct staff training

3. **Long-term Actions (1-3 months)**
   - Implement security governance
   - Enhance monitoring capabilities
   - Establish regular security assessments
"""

    def _generate_key_findings(self) -> str:
        key_findings = []
        for i, finding in enumerate(self.findings[:5], 1):
            key_findings.append(f"{i}. **{finding.get('title', 'Unknown')}**")
            key_findings.append(f"   - Severity: {finding.get('severity', 'unknown').upper()}")
            key_findings.append(f"   - {finding.get('description', 'No description')}")
        
        return '\n'.join(key_findings)

    def generate_technical_report(self) -> str:
        report = self.generate_executive_summary()
        
        report += "\n\n# Technical Details\n\n"
        report += "## Methodology\n\n"
        report += "The following testing methodologies were employed:\n"
        report += "- Automated vulnerability scanning\n"
        report += "- Manual penetration testing\n"
        report += "- Code review\n"
        report += "- Configuration analysis\n\n"
        
        report += "## Detailed Findings\n\n"
        
        for i, finding in enumerate(self.findings, 1):
            report += f"### {i}. {finding.get('title', 'Unknown')}\n\n"
            report += f"**Severity:** {finding.get('severity', 'unknown').upper()}\n"
            
            if self.config.get('include_cvss', True):
                cvss_score = self.calculate_cvss_score(finding)
                report += f"**CVSS Score:** {cvss_score}/10.0\n"
            
            report += f"**Affected System:** {finding.get('target', 'unknown')}\n\n"
            
            report += "**Description:**\n"
            report += f"{finding.get('description', 'No description')}\n\n"
            
            if self.config.get('include_poc', True) and finding.get('poc'):
                report += "**Proof of Concept:**\n"
                report += "```\n"
                report += finding['poc']
                report += "\n```\n\n"
            
            report += "**Remediation:**\n"
            report += f"{finding.get('remediation', 'No remediation provided')}\n\n"
            
            report += "**References:**\n"
            for ref in finding.get('references', []):
                report += f"- {ref}\n"
            report += "\n---\n\n"
        
        report += "## Appendix\n\n"
        report += "### Definitions\n"
        report += "- **Critical:** Can be exploited to completely compromise system\n"
        report += "- **High:** Can be exploited to compromise system with user interaction\n"
        report += "- **Medium:** Limited impact, requires specific conditions\n"
        report += "- **Low:** Minimal impact, difficult to exploit\n\n"
        
        return report

    def generate_report(self, output_format: str = 'markdown') -> str:
        if output_format == 'markdown':
            return self.generate_technical_report()
        elif output_format == 'json':
            return json.dumps({
                'metadata': self.metadata,
                'findings': self.findings
            }, indent=2)
        return self.generate_technical_report()

    def save_report(self, output_path: str):
        report = self.generate_report(self.config.get('report_format', 'markdown'))
        
        with open(output_path, 'w') as f:
            f.write(report)
        
        logger.info(f"Report saved to {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Penetration Test Report Generator')
    parser.add_argument('--findings', help='JSON file with findings')
    parser.add_argument('--output', required=True, help='Output report file')
    parser.add_argument('--config', help='Configuration file path (YAML/JSON)')
    parser.add_argument('--format', choices=['markdown', 'json'], default='markdown',
                        help='Report format')

    args = parser.parse_args()

    generator = ReportGenerator(args.config)
    
    if args.findings:
        generator.load_findings(args.findings)
    
    report = generator.generate_report(args.format)
    
    with open(args.output, 'w') as f:
        f.write(report)
    
    logger.info(f"Report generated: {args.output}")
    sys.exit(0)

if __name__ == '__main__':
    main()
