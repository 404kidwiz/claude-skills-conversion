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

class SASTScanner:
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
            'language': 'auto',
            'severity_threshold': 'medium',
            'exclude_patterns': ['venv', '__pycache__', '.git', 'node_modules']
        }

    def validate_inputs(self, path: str) -> bool:
        if not Path(path).exists():
            logger.error(f"Path does not exist: {path}")
            return False
        return True

    def detect_language(self, path: str) -> str:
        p = Path(path)
        
        if (p / 'package.json').exists():
            return 'javascript'
        elif (p / 'requirements.txt').exists() or (p / 'Pipfile').exists():
            return 'python'
        elif (p / 'pom.xml').exists():
            return 'java'
        elif (p / 'go.mod').exists():
            return 'go'
        elif (p / 'Cargo.toml').exists():
            return 'rust'
        elif (p / 'Gemfile').exists():
            return 'ruby'
        elif (p / 'composer.json').exists():
            return 'php'
        
        return 'python'

    def run_sonarqube_scan(self, path: str, language: str) -> List[Dict]:
        findings = []
        
        try:
            logger.info(f"Running SonarQube scan on {path} (language: {language})")
            
            sonar_properties = f"""
            sonar.projectKey=security-scan
            sonar.sources={path}
            sonar.language={language}
            """
            
            with open('sonar-project.properties', 'w') as f:
                f.write(sonar_properties)
            
            result = subprocess.run(
                ['sonar-scanner', '-Dsonar.host.url=http://localhost:9000'],
                capture_output=True,
                text=True,
                timeout=600
            )
            
            logger.info("SonarQube scan completed. Check dashboard for results.")
            
        except FileNotFoundError:
            logger.warning("SonarQube scanner not found. Visit: https://docs.sonarqube.org/")
        except subprocess.TimeoutExpired:
            logger.error("SonarQube scan timed out")
        except Exception as e:
            logger.error(f"Error running SonarQube: {str(e)}")

        return findings

    def run_semgrep_scan(self, path: str) -> List[Dict]:
        findings = []
        
        try:
            logger.info(f"Running Semgrep scan on {path}")
            result = subprocess.run(
                ['semgrep', '--config', 'auto', '--json', path],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.stdout:
                scan_data = json.loads(result.stdout)
                for result_item in scan_data.get('results', []):
                    severity = result_item.get('extra', {}).get('severity', 'INFO').lower()
                    if severity == 'error':
                        severity = 'high'
                    elif severity == 'warning':
                        severity = 'medium'
                    
                    findings.append({
                        'file': result_item.get('path', 'unknown'),
                        'line': result_item.get('start', {}).get('line', 0),
                        'rule_id': result_item.get('check_id', 'unknown'),
                        'severity': severity,
                        'message': result_item.get('message', 'No message'),
                        'category': result_item.get('extra', {}).get('metadata', {}).get('category', 'unknown')
                    })
        except FileNotFoundError:
            logger.warning("Semgrep not found. Install: https://semgrep.dev/docs/getting-started/")
        except subprocess.TimeoutExpired:
            logger.error("Semgrep scan timed out")
        except Exception as e:
            logger.error(f"Error running Semgrep: {str(e)}")

        return findings

    def run_codeql_scan(self, path: str, language: str) -> List[Dict]:
        findings = []
        
        try:
            logger.info(f"Running CodeQL scan on {path} (language: {language})")
            
            result = subprocess.run(
                ['codeql', 'database', 'create', 'codeql-db', '--language', language, '--source-root', path],
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode == 0:
                result = subprocess.run(
                    ['codeql', 'database', 'analyze', 'codeql-db', '--format=csv', '--output=codeql-results.csv'],
                    capture_output=True,
                    text=True,
                    timeout=600
                )
                
                logger.info("CodeQL scan completed. Check codeql-results.csv for results.")
                
        except FileNotFoundError:
            logger.warning("CodeQL not found. Install: https://codeql.github.com/docs/codeql-cli/")
        except subprocess.TimeoutExpired:
            logger.error("CodeQL scan timed out")
        except Exception as e:
            logger.error(f"Error running CodeQL: {str(e)}")

        return findings

    def scan(self, path: str = '.') -> Dict:
        if not self.validate_inputs(path):
            return self.results

        logger.info(f"Starting SAST scan on {path}")

        language = self.config.get('language', 'auto')
        if language == 'auto':
            language = self.detect_language(path)

        findings = []
        findings.extend(self.run_semgrep_scan(path))
        findings.extend(self.run_codeql_scan(path, language))
        
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
                        report.append(f"- {vuln.get('message', 'Unknown')}")
                        report.append(f"  File: {vuln.get('file')}:{vuln.get('line')}")
                        report.append(f"  Rule: {vuln.get('rule_id', 'unknown')}")
                        if vuln.get('category'):
                            report.append(f"  Category: {vuln['category']}")
            return "\n".join(report)
        return json.dumps(self.results, indent=2)

def main():
    parser = argparse.ArgumentParser(description='Static Application Security Testing (SAST) Scanner')
    parser.add_argument('path', nargs='?', default='.', help='Path to scan')
    parser.add_argument('--language', choices=['auto', 'python', 'javascript', 'java', 'go', 'rust', 'ruby', 'php'],
                        default='auto', help='Programming language')
    parser.add_argument('--config', help='Configuration file path (YAML/JSON)')
    parser.add_argument('--format', choices=['json', 'text'], default='json',
                        help='Output format')
    parser.add_argument('--output', help='Output file path')

    args = parser.parse_args()

    scanner = SASTScanner(args.config)
    if args.language != 'auto':
        scanner.config['language'] = args.language
    
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
        logger.error(f"Scan completed with {critical_vulns} high severity findings")
        sys.exit(1)
    elif total_vulns > 0:
        logger.warning(f"Scan completed with {total_vulns} total findings")
        sys.exit(0)
    else:
        logger.info("Scan completed - no findings")
        sys.exit(0)

if __name__ == '__main__':
    main()
