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

class WebAppTester:
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.findings = {
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
            'target_url': '',
            'auth_url': '',
            'auth_username': '',
            'auth_password': '',
            'scan_depth': 5,
            'spider_enabled': True,
            'active_scan_enabled': True
        }

    def validate_inputs(self, target_url: str) -> bool:
        if not target_url.startswith(('http://', 'https://')):
            logger.error(f"Invalid URL: {target_url}")
            return False
        return True

    def run_owasp_zap(self, target_url: str) -> List[Dict]:
        findings = []
        
        try:
            logger.info(f"Running OWASP ZAP on {target_url}")
            
            zap_options = ['-quickurl', target_url, '-quickout', 'zap_report.json']
            
            if self.config.get('spider_enabled', True):
                zap_options.append('-spider')
            
            result = subprocess.run(
                ['zap-cli'] + zap_options,
                capture_output=True,
                text=True,
                timeout=1800
            )
            
            if result.returncode == 0 and Path('zap_report.json').exists():
                with open('zap_report.json', 'r') as f:
                    zap_data = json.load(f)
                
                for site in zap_data.get('site', []):
                    for alert in site.get('alerts', []):
                        risk = alert.get('risk', 'info').lower()
                        if risk in ['critical', 'high', 'medium', 'low']:
                            findings.append({
                                'tool': 'owasp_zap',
                                'name': alert.get('name', 'Unknown'),
                                'severity': risk,
                                'url': alert.get('url', 'unknown'),
                                'description': alert.get('description', 'No description'),
                                'solution': alert.get('solution', 'No solution'),
                                ' CWE': alert.get('cweid', 'N/A'),
                                'references': alert.get('references', [])
                            })
                
                Path('zap_report.json').unlink()
                
        except FileNotFoundError:
            logger.warning("OWASP ZAP CLI not found. Install: pip install zap-cli")
        except subprocess.TimeoutExpired:
            logger.error("ZAP scan timed out")
        except Exception as e:
            logger.error(f"Error running ZAP: {str(e)}")

        return findings

    def run_burp_suite(self, target_url: str) -> List[Dict]:
        findings = []
        
        try:
            logger.info(f"Burp Suite requires manual configuration for {target_url}")
            logger.info("Use Burp Suite Professional API for automated scanning")
            
        except Exception as e:
            logger.error(f"Error with Burp Suite: {str(e)}")

        return findings

    def run_xsser(self, target_url: str) -> List[Dict]:
        findings = []
        
        try:
            logger.info(f"Running XSSer on {target_url}")
            result = subprocess.run(
                ['xsser', '--url', target_url, '--auto'],
                capture_output=True,
                text=True,
                timeout=600
            )
            
            findings.append({
                'tool': 'xsser',
                'target': target_url,
                'status': 'completed'
            })
            
        except FileNotFoundError:
            logger.warning("xsser not found. Install: sudo apt install xsser")
        except subprocess.TimeoutExpired:
            logger.error("XSSer scan timed out")
        except Exception as e:
            logger.error(f"Error running XSSer: {str(e)}")

        return findings

    def scan(self, target_url: str) -> Dict:
        if not self.validate_inputs(target_url):
            return self.findings

        logger.info(f"Starting web application security test on {target_url}")
        logger.warning("WARNING: Only test applications you own or have authorization to test")

        findings = []
        findings.extend(self.run_owasp_zap(target_url))
        findings.extend(self.run_burp_suite(target_url))
        findings.extend(self.run_xsser(target_url))

        for finding in findings:
            severity = finding.get('severity', 'low')
            if severity in self.findings:
                self.findings[severity].append(finding)

        logger.info(f"Web application test completed for {target_url}")
        return self.findings

    def generate_report(self, output_format: str = 'json') -> str:
        if output_format == 'json':
            return json.dumps(self.findings, indent=2)
        elif output_format == 'text':
            report = []
            for severity in ['critical', 'high', 'medium', 'low']:
                if self.findings[severity]:
                    report.append(f"\n{severity.upper()} Severity ({len(self.findings[severity])})")
                    report.append("=" * 50)
                    for vuln in self.findings[severity]:
                        report.append(f"- {vuln.get('name', 'Unknown')}")
                        report.append(f"  URL: {vuln.get('url', 'unknown')}")
                        report.append(f"  Tool: {vuln.get('tool', 'unknown')}")
                        if vuln.get(' CWE'):
                            report.append(f"  CWE: {vuln[' CWE']}")
            return "\n".join(report)
        return json.dumps(self.findings, indent=2)

def main():
    parser = argparse.ArgumentParser(description='Web Application Security Tester')
    parser.add_argument('url', help='Target URL')
    parser.add_argument('--config', help='Configuration file path (YAML/JSON)')
    parser.add_argument('--format', choices=['json', 'text'], default='json',
                        help='Output format')
    parser.add_argument('--output', help='Output file path')

    args = parser.parse_args()

    tester = WebAppTester(args.config)
    results = tester.scan(args.url)
    report = tester.generate_report(args.format)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        logger.info(f"Report saved to {args.output}")
    else:
        print(report)

    logger.info("Web application test completed")
    sys.exit(0)

if __name__ == '__main__':
    main()
