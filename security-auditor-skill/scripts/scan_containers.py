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

class ContainerScanner:
    def __init__(file_path):
        """
        Validate file path and read its contents before editing.
        """
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

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
            'dockerfile_paths': ['.'],
            'image_names': [],
            'severity_threshold': 'medium',
            'exclude_patterns': ['vendor', 'node_modules']
        }

    def validate_inputs(self, dockerfile_path: str) -> bool:
        if not Path(dockerfile_path).exists():
            logger.error(f"Dockerfile does not exist: {dockerfile_path}")
            return False
        return True

    def scan_dockerfile(self, dockerfile_path: str) -> List[Dict]:
        findings = []
        
        try:
            logger.info(f"Analyzing Dockerfile: {dockerfile_path}")
            result = subprocess.run(
                ['docker', 'build', '--no-cache', '-f', dockerfile_path, '-t', 'security-scan:temp', '.'],
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode != 0:
                logger.warning(f"Docker build failed, skipping image scan: {result.stderr}")
                return findings

            result = subprocess.run(
                ['trivy', 'image', '--format', 'json', '--severity', 'HIGH,CRITICAL,MEDIUM,LOW', 'security-scan:temp'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.stdout:
                scan_data = json.loads(result.stdout)
                for result_item in scan_data.get('Results', []):
                    for vuln in result_item.get('Vulnerabilities', []):
                        severity = vuln.get('Severity', 'unknown').lower()
                        if severity == 'critical':
                            severity = 'high'
                        
                        findings.append({
                            'dockerfile': dockerfile_path,
                            'package': result_item.get('Target', 'unknown'),
                            'vulnerability_id': vuln.get('VulnerabilityID', 'unknown'),
                            'severity': severity,
                            'cvss': vuln.get('CVSS', {}),
                            'description': vuln.get('Title', 'No description'),
                            'installed_version': vuln.get('InstalledVersion', 'unknown'),
                            'fixed_version': vuln.get('FixedVersion', 'none')
                        })

            subprocess.run(['docker', 'rmi', '-f', 'security-scan:temp'], capture_output=True)

        except FileNotFoundError:
            logger.warning("Docker or Trivy not found. Install Trivy: https://aquasecurity.github.io/trivy/")
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout scanning {dockerfile_path}")
        except Exception as e:
            logger.error(f"Error scanning {dockerfile_path}: {str(e)}")

        return findings

    def scan_image(self, image_name: str) -> List[Dict]:
        findings = []
        
        try:
            logger.info(f"Scanning Docker image: {image_name}")
            result = subprocess.run(
                ['trivy', 'image', '--format', 'json', '--severity', 'HIGH,CRITICAL,MEDIUM,LOW', image_name],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.stdout:
                scan_data = json.loads(result.stdout)
                for result_item in scan_data.get('Results', []):
                    for vuln in result_item.get('Vulnerabilities', []):
                        severity = vuln.get('Severity', 'unknown').lower()
                        if severity == 'critical':
                            severity = 'high'
                        
                        findings.append({
                            'image': image_name,
                            'package': result_item.get('Target', 'unknown'),
                            'vulnerability_id': vuln.get('VulnerabilityID', 'unknown'),
                            'severity': severity,
                            'cvss': vuln.get('CVSS', {}),
                            'description': vuln.get('Title', 'No description'),
                            'installed_version': vuln.get('InstalledVersion', 'unknown'),
                            'fixed_version': vuln.get('FixedVersion', 'none')
                        })
        except FileNotFoundError:
            logger.warning("Trivy not found. Install: https://aquasecurity.github.io/trivy/")
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout scanning {image_name}")
        except Exception as e:
            logger.error(f"Error scanning {image_name}: {str(e)}")

        return findings

    def scan_k8s_manifests(self, manifest_path: str = '.') -> List[Dict]:
        findings = []
        
        try:
            logger.info(f"Scanning Kubernetes manifests: {manifest_path}")
            result = subprocess.run(
                ['kube-bench', 'check', '--json', '--benchmark', 'cis-1.23'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.stdout:
                bench_data = json.loads(result.stdout)
                for test in bench_data.get('Tests', []):
                    for result_item in test.get('results', []):
                        if result_item.get('status') == 'FAIL':
                            findings.append({
                                'type': 'kubernetes',
                                'section': test.get('section', 'unknown'),
                                'test_number': result_item.get('test_number', 'unknown'),
                                'description': result_item.get('desc', 'No description'),
                                'remediation': result_item.get('remediation', 'No remediation'),
                                'severity': 'high'
                            })
        except FileNotFoundError:
            logger.warning("kube-bench not found. Install: https://github.com/aquasecurity/kube-bench")
        except subprocess.TimeoutExpired:
            logger.error("Timeout scanning Kubernetes manifests")
        except Exception as e:
            logger.error(f"Error scanning Kubernetes manifests: {str(e)}")

        return findings

    def scan(self, dockerfile_path: Optional[str] = None, image_name: Optional[str] = None) -> Dict:
        findings = []
        
        if dockerfile_path:
            if not self.validate_inputs(dockerfile_path):
                return self.results
            findings.extend(self.scan_dockerfile(dockerfile_path))
        
        if image_name:
            findings.extend(self.scan_image(image_name))
        
        if not dockerfile_path and not image_name:
            logger.info("Scanning for Dockerfiles in current directory")
            for dockerfile in Path('.').rglob('Dockerfile*'):
                findings.extend(self.scan_dockerfile(str(dockerfile)))

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
                        report.append(f"- {vuln.get('description', 'Unknown')}")
                        report.append(f"  Package: {vuln.get('package', 'unknown')}")
                        report.append(f"  ID: {vuln.get('vulnerability_id', 'unknown')}")
                        if vuln.get('fixed_version'):
                            report.append(f"  Fix: {vuln['fixed_version']}")
                        if vuln.get('remediation'):
                            report.append(f"  Remediation: {vuln['remediation']}")
            return "\n".join(report)
        return json.dumps(self.results, indent=2)

def main():
    parser = argparse.ArgumentParser(description='Container Security Scanner')
    parser.add_argument('--dockerfile', help='Dockerfile path to scan')
    parser.add_argument('--image', help='Docker image name to scan')
    parser.add_argument('--k8s', action='store_true', help='Scan Kubernetes manifests')
    parser.add_argument('--config', help='Configuration file path (YAML/JSON)')
    parser.add_argument('--format', choices=['json', 'text'], default='json',
                        help='Output format')
    parser.add_argument('--output', help='Output file path')

    args = parser.parse_args()

    scanner = ContainerScanner(args.config)
    results = scanner.scan(args.dockerfile, args.image)
    
    if args.k8s:
        k8s_results = scanner.scan_k8s_manifests()
        results['high'].extend(k8s_results)

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
