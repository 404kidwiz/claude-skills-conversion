#!/usr/bin/env python3
import subprocess
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
import argparse
import yaml
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class InfrastructureAuditor:
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.findings = []

    def _load_config(self, config_path: Optional[str]) -> Dict:
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        return {
            'terraform_paths': ['.'],
            'cloud_providers': ['aws', 'gcp', 'azure'],
            'severity_threshold': 'medium'
        }

    def validate_inputs(self, path: str) -> bool:
        if not Path(path).exists():
            logger.error(f"Path does not exist: {path}")
            return False
        return True

    def audit_terraform(self, tf_path: str) -> List[Dict]:
        findings = []
        
        try:
            logger.info(f"Auditing Terraform configuration: {tf_path}")
            result = subprocess.run(
                ['tfsec', '--format', 'json', tf_path],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.stdout:
                scan_data = json.loads(result.stdout)
                for check in scan_data.get('results', []):
                    findings.append({
                        'tool': 'terraform',
                        'file': check.get('location', {}).get('filename', 'unknown'),
                        'line': check.get('location', {}).get('start_line', 0),
                        'rule_id': check.get('rule_id', 'unknown'),
                        'severity': check.get('severity', 'unknown'),
                        'description': check.get('description', 'No description'),
                        'impact': check.get('impact', 'No impact specified'),
                        'resolution': check.get('resolution', 'No resolution specified')
                    })
        except FileNotFoundError:
            logger.warning("tfsec not found. Install: https://github.com/aquasecurity/tfsec")
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout auditing {tf_path}")
        except Exception as e:
            logger.error(f"Error auditing {tf_path}: {str(e)}")

        return findings

    def audit_cloudformation(self, cf_path: str) -> List[Dict]:
        findings = []
        
        try:
            logger.info(f"Auditing CloudFormation template: {cf_path}")
            result = subprocess.run(
                ['cfn_nag', '--output-format', 'json', cf_path],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.stdout:
                scan_data = json.loads(result.stdout)
                for failure in scan_data.get('failures', []):
                    findings.append({
                        'tool': 'cloudformation',
                        'file': cf_path,
                        'line': failure.get('line_number', 0),
                        'rule_id': failure.get('id', 'unknown'),
                        'severity': failure.get('severity', 'unknown'),
                        'description': failure.get('message', 'No description')
                    })
        except FileNotFoundError:
            logger.warning("cfn-nag not found. Install: https://github.com/stelligent/cfn_nag")
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout auditing {cf_path}")
        except Exception as e:
            logger.error(f"Error auditing {cf_path}: {str(e)}")

        return findings

    def audit_ansible(self, playbook_path: str) -> List[Dict]:
        findings = []
        
        try:
            logger.info(f"Auditing Ansible playbook: {playbook_path}")
            result = subprocess.run(
                ['ansible-lint', '--parseable', playbook_path],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.stdout:
                for line in result.stdout.split('\n'):
                    if line.strip():
                        match = re.match(r'^(.+):(\d+): \[(.+)\] (.+)$', line)
                        if match:
                            findings.append({
                                'tool': 'ansible',
                                'file': match.group(1),
                                'line': int(match.group(2)),
                                'rule_id': match.group(3),
                                'severity': 'medium',
                                'description': match.group(4)
                            })
        except FileNotFoundError:
            logger.warning("ansible-lint not found. Install: pip install ansible-lint")
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout auditing {playbook_path}")
        except Exception as e:
            logger.error(f"Error auditing {playbook_path}: {str(e)}")

        return findings

    def audit_kubernetes(self, k8s_path: str) -> List[Dict]:
        findings = []
        
        try:
            logger.info(f"Auditing Kubernetes manifests: {k8s_path}")
            result = subprocess.run(
                ['kubesec', 'scan', k8s_path],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.stdout:
                scan_data = json.loads(result.stdout)
                for resource in scan_data:
                    score = resource.get('score', 0)
                    for finding in resource.get('scoring', {}).get('advise', []):
                        findings.append({
                            'tool': 'kubernetes',
                            'file': resource.get('file', 'unknown'),
                            'resource': resource.get('kind', 'unknown'),
                            'name': resource.get('metadata', {}).get('name', 'unknown'),
                            'severity': 'high' if score < 5 else 'medium',
                            'description': finding,
                            'score': score
                        })
        except FileNotFoundError:
            logger.warning("kubesec not found. Install: https://kubesec.io/")
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout auditing {k8s_path}")
        except Exception as e:
            logger.error(f"Error auditing {k8s_path}: {str(e)}")

        return findings

    def audit(self, path: str = '.') -> List[Dict]:
        if not self.validate_inputs(path):
            return self.findings

        logger.info(f"Starting infrastructure audit on {path}")

        p = Path(path)

        for tf_file in p.rglob('*.tf'):
            self.findings.extend(self.audit_terraform(str(tf_file)))

        for cf_file in p.rglob('*.yaml'):
            if 'cloudformation' in str(cf_file).lower() or cf_file.parent.name == 'cloudformation':
                self.findings.extend(self.audit_cloudformation(str(cf_file)))

        for playbook in p.rglob('*.yml'):
            if 'ansible' in str(playbook).lower() or playbook.parent.name == 'ansible':
                self.findings.extend(self.audit_ansible(str(playbook)))

        for k8s_file in p.rglob('*.yaml'):
            if 'kubernetes' in str(k8s_file).lower() or 'k8s' in str(k8s_file).lower():
                self.findings.extend(self.audit_kubernetes(str(k8s_file)))

        logger.info(f"Found {len(self.findings)} infrastructure issues")
        return self.findings

    def generate_report(self, output_format: str = 'json') -> str:
        if output_format == 'json':
            return json.dumps(self.findings, indent=2)
        elif output_format == 'text':
            report = []
            for finding in self.findings:
                report.append(f"\n{finding.get('file', 'unknown')}:{finding.get('line', 0)}")
                report.append(f"  Tool: {finding.get('tool', 'unknown')}")
                report.append(f"  Rule: {finding.get('rule_id', 'unknown')}")
                report.append(f"  Severity: {finding.get('severity', 'unknown').upper()}")
                report.append(f"  Description: {finding.get('description', 'No description')}")
                if finding.get('resolution'):
                    report.append(f"  Resolution: {finding['resolution']}")
            return "\n".join(report)
        return json.dumps(self.findings, indent=2)

def main():
    parser = argparse.ArgumentParser(description='Infrastructure Security Auditor')
    parser.add_argument('path', nargs='?', default='.', help='Path to audit')
    parser.add_argument('--config', help='Configuration file path (YAML/JSON)')
    parser.add_argument('--format', choices=['json', 'text'], default='json',
                        help='Output format')
    parser.add_argument('--output', help='Output file path')

    args = parser.parse_args()

    auditor = InfrastructureAuditor(args.config)
    results = auditor.audit(args.path)
    report = auditor.generate_report(args.format)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        logger.info(f"Report saved to {args.output}")
    else:
        print(report)

    high_severity = sum(1 for f in results if f.get('severity', '').lower() == 'high')
    
    if high_severity > 0:
        logger.error(f"Found {high_severity} high severity issues")
        sys.exit(1)
    elif len(results) > 0:
        logger.warning(f"Found {len(results)} total issues")
        sys.exit(0)
    else:
        logger.info("No infrastructure issues found")
        sys.exit(0)

if __name__ == '__main__':
    main()
