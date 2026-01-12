#!/usr/bin/env python3
import subprocess
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
import argparse
import yaml

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VulnerabilityScanner:
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.results = {
            'high': [],
            'medium': [],
            'low': [],
            'info': []
        }

    def _load_config(self, config_path: Optional[str]) -> Dict:
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        return {
            'scan_paths': ['.'],
            'exclude_patterns': ['venv', '__pycache__', '.git'],
            'severity_threshold': 'medium'
        }

    def validate_inputs(self, scan_path: str) -> bool:
        if not Path(scan_path).exists():
            logger.error(f"Path does not exist: {scan_path}")
            return False
        return True

    def run_bandit_scan(self, path: str) -> Dict:
        try:
            logger.info(f"Running Bandit scan on {path}")
            result = subprocess.run(
                ['bandit', '-r', path, '-f', 'json'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            elif result.returncode == 1:
                return json.loads(result.stdout)
            else:
                logger.warning(f"Bandit scan failed: {result.stderr}")
                return {'results': []}
        except subprocess.TimeoutExpired:
            logger.error("Bandit scan timed out")
            return {'results': []}
        except Exception as e:
            logger.error(f"Error running Bandit: {str(e)}")
            return {'results': []}

    def run_safety_scan(self, requirements_file: str) -> List[Dict]:
        try:
            logger.info(f"Running Safety scan on {requirements_file}")
            result = subprocess.run(
                ['safety', 'check', '-r', requirements_file, '--json'],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                logger.warning(f"Safety scan found vulnerabilities")
                return json.loads(result.stdout) if result.stdout else []
        except Exception as e:
            logger.error(f"Error running Safety: {str(e)}")
            return []

    def categorize_vulnerability(self, vuln: Dict) -> str:
        severity = vuln.get('issue_severity', 'info').lower()
        if severity in ['high', 'critical']:
            return 'high'
        elif severity == 'medium':
            return 'medium'
        elif severity == 'low':
            return 'low'
        return 'info'

    def scan(self, scan_path: str = '.') -> Dict:
        if not self.validate_inputs(scan_path):
            return self.results

        logger.info(f"Starting vulnerability scan on {scan_path}")

        path = Path(scan_path)

        if path.is_file() and path.suffix in ['.txt', 'in']:
            dep_vulns = self.run_safety_scan(str(path))
            for vuln in dep_vulns:
                category = self.categorize_vulnerability(vuln)
                self.results[category].append({
                    'type': 'dependency',
                    'package': vuln.get('package', 'unknown'),
                    'vulnerability_id': vuln.get('id', 'unknown'),
                    'severity': category,
                    'description': vuln.get('advisory', 'No description')
                })
        else:
            code_vulns = self.run_bandit_scan(str(path))
            for vuln in code_vulns.get('results', []):
                category = self.categorize_vulnerability(vuln)
                self.results[category].append({
                    'type': 'code',
                    'file': vuln.get('filename', 'unknown'),
                    'line': vuln.get('line_number', 0),
                    'test_id': vuln.get('test_id', 'unknown'),
                    'severity': category,
                    'description': vuln.get('issue_text', 'No description')
                })

        return self.results

    def generate_report(self, output_format: str = 'json') -> str:
        if output_format == 'json':
            return json.dumps(self.results, indent=2)
        elif output_format == 'text':
            report = []
            for severity in ['high', 'medium', 'low', 'info']:
                if self.results[severity]:
                    report.append(f"\n{severity.upper()} SEVERITY ({len(self.results[severity])})")
                    report.append("=" * 50)
                    for vuln in self.results[severity]:
                        report.append(f"- {vuln.get('description', 'Unknown')}")
                        if vuln.get('file'):
                            report.append(f"  File: {vuln.get('file')}:{vuln.get('line')}")
                        if vuln.get('package'):
                            report.append(f"  Package: {vuln.get('package')}")
            return "\n".join(report)
        return json.dumps(self.results, indent=2)

def main():
    parser = argparse.ArgumentParser(description='Security Vulnerability Scanner')
    parser.add_argument('path', nargs='?', default='.', help='Path to scan')
    parser.add_argument('--config', help='Configuration file path (YAML/JSON)')
    parser.add_argument('--format', choices=['json', 'text'], default='json',
                        help='Output format')
    parser.add_argument('--output', help='Output file path')

    args = parser.parse_args()

    scanner = VulnerabilityScanner(args.config)
    results = scanner.scan(args.path)
    report = scanner.generate_report(args.format)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        logger.info(f"Report saved to {args.output}")
    else:
        print(report)

    total_vulns = sum(len(v) for v in results.values())
    critical_vulns = len(results.get('high', []))
    
    if critical_vulns > 0:
        logger.error(f"Scan completed with {critical_vulns} high severity vulnerabilities")
        sys.exit(1)
    elif total_vulns > 0:
        logger.warning(f"Scan completed with {total_vulns} total vulnerabilities")
        sys.exit(0)
    else:
        logger.info("Scan completed - no vulnerabilities found")
        sys.exit(0)

if __name__ == '__main__':
    main()
