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

class DependencyAuditor:
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.vulnerabilities = []

    def _load_config(self, config_path: Optional[str]) -> Dict:
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        return {
            'scan_paths': ['.'],
            'requirements_files': ['requirements.txt', 'requirements-dev.txt', 'Pipfile', 'pyproject.toml'],
            'package_files': ['package.json', 'yarn.lock', 'package-lock.json', 'composer.json', 'Gemfile'],
            'severity_threshold': 'medium'
        }

    def validate_inputs(self, scan_path: str) -> bool:
        if not Path(scan_path).exists():
            logger.error(f"Path does not exist: {scan_path}")
            return False
        return True

    def audit_python_deps(self, path: str) -> List[Dict]:
        results = []
        
        requirements_files = []
        p = Path(path)
        
        for req_file in self.config.get('requirements_files', []):
            if (p / req_file).exists():
                requirements_files.append(p / req_file)
        
        for req_file in p.rglob('*.txt'):
            if 'requirement' in req_file.name.lower():
                requirements_files.append(req_file)

        for req_file in p.rglob('Pipfile'):
            requirements_files.append(req_file)

        for req_file in p.rglob('pyproject.toml'):
            requirements_files.append(req_file)

        for req_file in requirements_files:
            try:
                logger.info(f"Auditing Python dependencies: {req_file}")
                result = subprocess.run(
                    ['pip-audit', '--desc', '--format', 'json', '--requirement', str(req_file)],
                    capture_output=True,
                    text=True,
                    timeout=180
                )
                
                if result.stdout:
                    vulns = json.loads(result.stdout)
                    for vuln in vulns:
                        results.append({
                            'file': str(req_file),
                            'package': vuln.get('name', 'unknown'),
                            'installed_version': vuln.get('version', 'unknown'),
                            'vulnerability_id': vuln.get('id', 'unknown'),
                            'severity': vuln.get('severity', 'unknown'),
                            'description': vuln.get('description', 'No description'),
                            'fix_versions': vuln.get('fix_versions', []),
                            'ecosystem': 'python'
                        })
            except FileNotFoundError:
                logger.warning("pip-audit not found. Install with: pip install pip-audit")
            except subprocess.TimeoutExpired:
                logger.error(f"Timeout auditing {req_file}")
            except Exception as e:
                logger.error(f"Error auditing {req_file}: {str(e)}")

        return results

    def audit_nodejs_deps(self, path: str) -> List[Dict]:
        results = []
        p = Path(path)

        for pkg_file in self.config.get('package_files', []):
            pkg_path = p / pkg_file
            if not pkg_path.exists():
                continue

            try:
                logger.info(f"Auditing Node.js dependencies: {pkg_file}")
                result = subprocess.run(
                    ['npm', 'audit', '--json'],
                    capture_output=True,
                    text=True,
                    cwd=str(pkg_path.parent),
                    timeout=120
                )

                if result.stdout:
                    audit_data = json.loads(result.stdout)
                    vulns = audit_data.get('vulnerabilities', {})
                    
                    for package_name, vuln_data in vulns.items():
                        severity = vuln_data.get('severity', 'unknown')
                        results.append({
                            'file': str(pkg_file),
                            'package': package_name,
                            'severity': severity,
                            'title': vuln_data.get('title', 'No title'),
                            'description': vuln_data.get('via', []),
                            'patches': vuln_data.get('patches', []),
                            'ecosystem': 'nodejs'
                        })
            except FileNotFoundError:
                logger.warning("npm not found")
            except subprocess.TimeoutExpired:
                logger.error(f"Timeout auditing {pkg_file}")
            except Exception as e:
                logger.error(f"Error auditing {pkg_file}: {str(e)}")

        return results

    def audit_ruby_deps(self, path: str) -> List[Dict]:
        results = []
        p = Path(path)

        for gemfile in p.rglob('Gemfile'):
            try:
                logger.info(f"Auditing Ruby dependencies: {gemfile}")
                result = subprocess.run(
                    ['bundle', 'audit', '--check', '--format', 'json'],
                    capture_output=True,
                    text=True,
                    cwd=str(gemfile.parent),
                    timeout=180
                )

                if result.stdout:
                    vulns = json.loads(result.stdout)
                    for vuln in vulns:
                        results.append({
                            'file': str(gemfile),
                            'package': vuln.get('gem', 'unknown'),
                            'vulnerability_id': vuln.get('id', 'unknown'),
                            'severity': vuln.get('severity', 'unknown'),
                            'description': vuln.get('description', 'No description'),
                            'patched_versions': vuln.get('patched_versions', []),
                            'ecosystem': 'ruby'
                        })
            except FileNotFoundError:
                logger.warning("bundle-audit not found. Install with: gem install bundler-audit")
            except subprocess.TimeoutExpired:
                logger.error(f"Timeout auditing {gemfile}")
            except Exception as e:
                logger.error(f"Error auditing {gemfile}: {str(e)}")

        return results

    def audit(self, scan_path: str = '.') -> List[Dict]:
        if not self.validate_inputs(scan_path):
            return self.vulnerabilities

        logger.info(f"Starting dependency audit on {scan_path}")

        results = []
        results.extend(self.audit_python_deps(scan_path))
        results.extend(self.audit_nodejs_deps(scan_path))
        results.extend(self.audit_ruby_deps(scan_path))

        self.vulnerabilities = results
        logger.info(f"Found {len(results)} dependency vulnerabilities")
        return results

    def generate_report(self, output_format: str = 'json') -> str:
        if output_format == 'json':
            return json.dumps(self.vulnerabilities, indent=2)
        elif output_format == 'text':
            report = []
            for vuln in self.vulnerabilities:
                report.append(f"\n{vuln.get('package', 'unknown')} ({vuln.get('ecosystem', 'unknown')})")
                report.append(f"  Severity: {vuln.get('severity', 'unknown').upper()}")
                report.append(f"  File: {vuln.get('file', 'unknown')}")
                if vuln.get('vulnerability_id'):
                    report.append(f"  ID: {vuln['vulnerability_id']}")
                report.append(f"  Description: {vuln.get('description', 'No description')}")
                if vuln.get('fix_versions'):
                    report.append(f"  Fix versions: {', '.join(vuln['fix_versions'])}")
            return "\n".join(report)
        return json.dumps(self.vulnerabilities, indent=2)

def main():
    parser = argparse.ArgumentParser(description='Dependency Vulnerability Auditor')
    parser.add_argument('path', nargs='?', default='.', help='Path to audit')
    parser.add_argument('--config', help='Configuration file path (YAML/JSON)')
    parser.add_argument('--format', choices=['json', 'text'], default='json',
                        help='Output format')
    parser.add_argument('--output', help='Output file path')

    args = parser.parse_args()

    auditor = DependencyAuditor(args.config)
    results = auditor.audit(args.path)
    report = auditor.generate_report(args.format)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        logger.info(f"Report saved to {args.output}")
    else:
        print(report)

    high_severity = sum(1 for v in results if v.get('severity', '').lower() in ['high', 'critical'])
    
    if high_severity > 0:
        logger.error(f"Found {high_severity} high/critical severity vulnerabilities")
        sys.exit(1)
    elif len(results) > 0:
        logger.warning(f"Found {len(results)} total vulnerabilities")
        sys.exit(0)
    else:
        logger.info("No dependency vulnerabilities found")
        sys.exit(0)

if __name__ == '__main__':
    main()
