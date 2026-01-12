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

class DASTScanner:
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
            'target_url': '',
            'auth_url': '',
            'auth_username': '',
            'auth_password': '',
            'scan_depth': 5,
            'severity_threshold': 'medium',
            'include_spider': True
        }

    def validate_inputs(self, target_url: str) -> bool:
        if not target_url.startswith(('http://', 'https://')):
            logger.error(f"Invalid URL: {target_url}")
            return False
        return True

    def run_owasp_zap(self, target_url: str) -> List[Dict]:
        findings = []
        
        try:
            logger.info(f"Starting OWASP ZAP scan on {target_url}")
            
            zap_scan_options = [
                '-quickurl', target_url,
                '-quickout', 'zap_report.json',
                '-config', f'scan.maxdepth={self.config.get("scan_depth", 5)}'
            ]
            
            if self.config.get('include_spider', True):
                zap_scan_options.extend(['-spider'])
            
            result = subprocess.run(
                ['zap-cli'] + zap_scan_options,
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
                        if risk == 'high':
                            severity = 'high'
                        elif risk == 'medium':
                            severity = 'medium'
                        elif risk == 'low':
                            severity = 'low'
                        else:
                            severity = 'info'
                        
                        findings.append({
                            'url': alert.get('url', 'unknown'),
                            'name': alert.get('name', 'unknown'),
                            'severity': severity,
                            'description': alert.get('description', 'No description'),
                            'solution': alert.get('solution', 'No solution'),
                            'confidence': alert.get('confidence', 'unknown'),
                            ' CWE': alert.get('cweid', 'N/A')
                        })
                
                Path('zap_report.json').unlink()
            else:
                logger.warning(f"ZAP scan completed with issues: {result.stderr}")
                
        except FileNotFoundError:
            logger.warning("OWASP ZAP CLI not found. Install: https://github.com/zaproxy/zaproxy")
        except subprocess.TimeoutExpired:
            logger.error("ZAP scan timed out")
        except Exception as e:
            logger.error(f"Error running ZAP: {str(e)}")

        return findings

    def run_nikto(self, target_url: str) -> List[Dict]:
        findings = []
        
        try:
            logger.info(f"Running Nikto scan on {target_url}")
            result = subprocess.run(
                ['nikto', '-h', target_url, '-Format', 'json', '-output', 'nikto_report.json'],
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if Path('nikto_report.json').exists():
                with open('nikto_report.json', 'r') as f:
                    nikto_data = json.load(f)
                
                for vuln in nikto_data.get('vulnerabilities', []):
                    findings.append({
                        'url': target_url,
                        'name': vuln.get('name', 'unknown'),
                        'severity': 'medium',
                        'description': vuln.get('description', 'No description'),
                        'references': vuln.get('references', [])
                    })
                
                Path('nikto_report.json').unlink()
                
        except FileNotFoundError:
            logger.warning("Nikto not found. Install: https://github.com/sullo/nikto")
        except subprocess.TimeoutExpired:
            logger.error("Nikto scan timed out")
        except Exception as e:
            logger.error(f"Error running Nikto: {str(e)}")

        return findings

    def run_sqlmap(self, target_url: str) -> List[Dict]:
        findings = []
        
        try:
            logger.info(f"Running SQLMap scan on {target_url}")
            result = subprocess.run(
                ['sqlmap', '-u', target_url, '--batch', '--json-output'],
                capture_output=True,
                text=True,
                timeout=600
            )
            
            logger.info("SQLMap scan completed. Review the output for SQL injection vulnerabilities.")
            
        except FileNotFoundError:
            logger.warning("SQLMap not found. Install: https://sqlmap.org/")
        except subprocess.TimeoutExpired:
            logger.error("SQLMap scan timed out")
        except Exception as e:
            logger.error(f"Error running SQLMap: {str(e)}")

        return findings

    def run_burp(self, target_url: str) -> List[Dict]:
        findings = []
        
        try:
            logger.info(f"Burp Suite requires manual configuration for target: {target_url}")
            logger.info("Use Burp Suite Professional API for automated scanning")
            
        except Exception as e:
            logger.error(f"Error with Burp Suite: {str(e)}")

        return findings

    def scan(self, target_url: str) -> Dict:
        if not self.validate_inputs(target_url):
            return self.results

        logger.info(f"Starting DAST scan on {target_url}")
        logger.warning("WARNING: Only scan targets you own or have authorization to test")

        findings = []
        findings.extend(self.run_owasp_zap(target_url))
        findings.extend(self.run_nikto(target_url))
        findings.extend(self.run_sqlmap(target_url))
        
        for finding in findings:
            severity = finding.get('severity', 'info')
            self.results[severity].append(finding)

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
                        report.append(f"- {vuln.get('name', 'Unknown')}")
                        report.append(f"  URL: {vuln.get('url', 'unknown')}")
                        report.append(f"  Description: {vuln.get('description', 'No description')}")
                        if vuln.get('solution'):
                            report.append(f"  Solution: {vuln['solution']}")
            return "\n".join(report)
        return json.dumps(self.results, indent=2)

def main():
    parser = argparse.ArgumentParser(description='Dynamic Application Security Testing (DAST) Scanner')
    parser.add_argument('url', help='Target URL to scan')
    parser.add_argument('--config', help='Configuration file path (YAML/JSON)')
    parser.add_argument('--format', choices=['json', 'text'], default='json',
                        help='Output format')
    parser.add_argument('--output', help='Output file path')

    args = parser.parse_args()

    scanner = DASTScanner(args.config)
    results = scanner.scan(args.url)
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
