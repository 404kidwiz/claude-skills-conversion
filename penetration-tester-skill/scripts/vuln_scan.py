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

class VulnerabilityScanner:
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.vulnerabilities = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }

    def _load_config(self, config_path: Optional[str]) -> Dict:
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        return {
            'scan_types': ['network', 'web', 'application'],
            'severity_threshold': 'medium',
            'aggressive_scan': False
        }

    def validate_inputs(self, target: str) -> bool:
        if not target:
            logger.error("Target is required")
            return False
        return True

    def run_nessus_scan(self, target: str) -> List[Dict]:
        findings = []
        
        try:
            logger.info(f"Running Nessus scan on {target}")
            result = subprocess.run(
                ['nessuscli', 'scan', 'new', '--targets', target, '--name', f'scan_{target}'],
                capture_output=True,
                text=True,
                timeout=600
            )
            
            logger.info("Nessus scan initiated. Check Nessus UI for results.")
            
        except FileNotFoundError:
            logger.warning("Nessus CLI not found")
        except subprocess.TimeoutExpired:
            logger.error("Nessus scan timed out")
        except Exception as e:
            logger.error(f"Error running Nessus: {str(e)}")

        return findings

    def run_openvas_scan(self, target: str) -> List[Dict]:
        findings = []
        
        try:
            logger.info(f"Running OpenVAS scan on {target}")
            result = subprocess.run(
                ['omp', '-i', f'X<create_task><name>scan_{target}</name>'
                 f'<target hosts="{target}"/></create_task>'],
                capture_output=True,
                text=True,
                timeout=600
            )
            
            logger.info("OpenVAS scan initiated. Check OpenVAS dashboard for results.")
            
        except FileNotFoundError:
            logger.warning("OpenVAS (gvm) CLI not found")
        except subprocess.TimeoutExpired:
            logger.error("OpenVAS scan timed out")
        except Exception as e:
            logger.error(f"Error running OpenVAS: {str(e)}")

        return findings

    def run_nmap_vuln_scan(self, target: str) -> List[Dict]:
        findings = []
        
        try:
            logger.info(f"Running Nmap vulnerability scan on {target}")
            result = subprocess.run(
                ['nmap', '--script', 'vuln', '-p-', '-T4', 
                 '-oX', f'{target}_vuln.xml', target],
                capture_output=True,
                text=True,
                timeout=1800
            )
            
            findings.append({
                'tool': 'nmap',
                'scan_type': 'vulnerability',
                'target': target,
                'status': 'completed' if result.returncode == 0 else 'failed'
            })
            
        except FileNotFoundError:
            logger.warning("nmap not found. Install: sudo apt install nmap")
        except subprocess.TimeoutExpired:
            logger.error("Nmap scan timed out")
        except Exception as e:
            logger.error(f"Error running Nmap: {str(e)}")

        return findings

    def categorize_severity(self, severity: str) -> str:
        severity_map = {
            'critical': 'critical',
            'high': 'high',
            'medium': 'medium',
            'low': 'low',
            'info': 'low',
            'none': 'low'
        }
        return severity_map.get(severity.lower(), 'low')

    def scan(self, target: str) -> Dict:
        if not self.validate_inputs(target):
            return self.vulnerabilities

        logger.info(f"Starting vulnerability scan on {target}")
        logger.warning("WARNING: Only scan targets you own or have authorization to test")

        findings = []
        
        findings.extend(self.run_nmap_vuln_scan(target))
        findings.extend(self.run_nessus_scan(target))
        findings.extend(self.run_openvas_scan(target))

        for finding in findings:
            severity = finding.get('severity', 'low')
            if severity in self.vulnerabilities:
                self.vulnerabilities[severity].append(finding)

        logger.info(f"Vulnerability scan completed for {target}")
        return self.vulnerabilities

    def generate_report(self, output_format: str = 'json') -> str:
        if output_format == 'json':
            return json.dumps(self.vulnerabilities, indent=2)
        elif output_format == 'text':
            report = []
            for severity in ['critical', 'high', 'medium', 'low']:
                if self.vulnerabilities[severity]:
                    report.append(f"\n{severity.upper()} Severity ({len(self.vulnerabilities[severity])})")
                    report.append("=" * 50)
                    for vuln in self.vulnerabilities[severity]:
                        report.append(f"- {vuln.get('description', 'Unknown vulnerability')}")
                        if vuln.get('tool'):
                            report.append(f"  Tool: {vuln['tool']}")
            return "\n".join(report)
        return json.dumps(self.vulnerabilities, indent=2)

def main():
    parser = argparse.ArgumentParser(description='Vulnerability Scanner for Penetration Testing')
    parser.add_argument('target', help='Target to scan')
    parser.add_argument('--config', help='Configuration file path (YAML/JSON)')
    parser.add_argument('--format', choices=['json', 'text'], default='json',
                        help='Output format')
    parser.add_argument('--output', help='Output file path')

    args = parser.parse_args()

    scanner = VulnerabilityScanner(args.config)
    results = scanner.scan(args.target)
    report = scanner.generate_report(args.format)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        logger.info(f"Report saved to {args.output}")
    else:
        print(report)

    logger.info("Vulnerability scan completed")
    sys.exit(0)

if __name__ == '__main__':
    main()
