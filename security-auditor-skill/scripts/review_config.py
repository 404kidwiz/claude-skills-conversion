#!/usr/bin/env python3
import re
import sys
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

class ConfigReviewer:
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.findings = []

    def _load_config(self, config_path: Optional[str]) -> Dict:
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        return {
            'scan_paths': ['.'],
            'exclude_patterns': ['venv', '__pycache__', '.git', 'node_modules'],
            'file_extensions': ['.py', '.js', '.ts', '.java', '.go', '.rb', '.php', '.sh', '.yml', '.yaml', '.json', '.env', '.config', '.conf'],
            'check_for_secrets': True,
            'check_for_weak_passwords': True,
            'check_for_insecure_defaults': True
        }

    def validate_inputs(self, path: str) -> bool:
        if not Path(path).exists():
            logger.error(f"Path does not exist: {path}")
            return False
        return True

    def check_hardcoded_credentials(self, file_path: Path, content: str, lines: List[str]) -> List[Dict]:
        findings = []
        
        password_patterns = [
            r'password\s*=\s*["\']([^"\s\'\)]{8,})["\']',
            r'passwd\s*=\s*["\']([^"\s\'\)]{8,})["\']',
            r'secret\s*=\s*["\']([^"\s\'\)]{8,})["\']',
            r'api_key\s*=\s*["\']([^"\s\'\)]{16,})["\']',
            r'apikey\s*=\s*["\']([^"\s\'\)]{16,})["\']',
            r'token\s*=\s*["\']([^"\s\'\)]{20,})["\']'
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern in password_patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    value = match.group(1)
                    if len(value) < 12:
                        continue
                    findings.append({
                        'file': str(file_path),
                        'line': line_num,
                        'issue': 'hardcoded_credential',
                        'severity': 'high',
                        'pattern': pattern,
                        'context': line.strip()[:100],
                        'recommendation': 'Move to environment variables or secret management system'
                    })
        
        return findings

    def check_weak_password_defaults(self, file_path: Path, content: str, lines: List[str]) -> List[Dict]:
        findings = []
        
        weak_defaults = [
            r'password\s*=\s*["\']?(admin|password|123456|qwerty|letmein|welcome)["\']?',
            r'default_password\s*=\s*["\']?(admin|password|123456|qwerty|letmein|welcome)["\']?',
            r'root_password\s*=\s*["\']?(admin|password|123456|qwerty|letmein|welcome)["\']?'
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern in weak_defaults:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append({
                        'file': str(file_path),
                        'line': line_num,
                        'issue': 'weak_password_default',
                        'severity': 'high',
                        'context': line.strip()[:100],
                        'recommendation': 'Use strong, unique default passwords and require change on first login'
                    })
        
        return findings

    def check_insecure_defaults(self, file_path: Path, content: str, lines: List[str]) -> List[Dict]:
        findings = []
        
        insecure_patterns = {
            'debug_mode': r'(debug|DEBUG)\s*=\s*True',
            'ssl_verify_false': r'(verify|ssl_verify|SSL_VERIFY)\s*=\s*False',
            'http_allowed': r'allowed_hosts\s*=\s*["\']?\*["\']?',
            'cors_all': r'(cors|CORS).*\*',
            'empty_token': r'jwt_secret\s*=\s*["\']?["\']?',
            'insecure_cipher': r'(cipher|encryption).*=(des|md5|sha1)',
            'disable_auth': r'(auth|authentication).*=.*False',
            'allow_all': r'allow\s*=\s*["\']?\*["\']?',
            'sql_raw': r'execute\(["\'].*%.*["\']',
            'eval_usage': r'\beval\('
        }
        
        for line_num, line in enumerate(lines, 1):
            for issue_type, pattern in insecure_patterns.items():
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append({
                        'file': str(file_path),
                        'line': line_num,
                        'issue': issue_type,
                        'severity': 'medium',
                        'context': line.strip()[:100],
                        'recommendation': f'Review and secure {issue_type.replace("_", " ")} configuration'
                    })
        
        return findings

    def check_exposed_config_files(self, file_path: Path) -> List[Dict]:
        findings = []
        
        sensitive_filenames = [
            '.env', '.env.local', '.env.development', '.env.production',
            'config.json', 'secrets.json', 'credentials.json',
            'id_rsa', 'id_ed25519', '.pem', '.key', '.crt'
        ]
        
        if file_path.name.lower() in sensitive_filenames:
            findings.append({
                'file': str(file_path),
                'line': 0,
                'issue': 'exposed_config_file',
                'severity': 'medium',
                'context': f'Sensitive configuration file: {file_path.name}',
                'recommendation': 'Ensure this file is in .gitignore and use environment variables'
            })
        
        return findings

    def check_logging_exposure(self, file_path: Path, content: str, lines: List[str]) -> List[Dict]:
        findings = []
        
        logging_patterns = [
            r'log\.(info|debug|warning|error)\(["\'].*password',
            r'print\(["\'].*password',
            r'console\.log\(["\'].*password',
            r'logger\.info\(["\'].*token'
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern in logging_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append({
                        'file': str(file_path),
                        'line': line_num,
                        'issue': 'logging_sensitive_data',
                        'severity': 'medium',
                        'context': line.strip()[:100],
                        'recommendation': 'Avoid logging sensitive information like passwords or tokens'
                    })
        
        return findings

    def review_file(self, file_path: Path) -> List[Dict]:
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
                if self.config.get('check_for_secrets', True):
                    findings.extend(self.check_hardcoded_credentials(file_path, content, lines))
                
                if self.config.get('check_for_weak_passwords', True):
                    findings.extend(self.check_weak_password_defaults(file_path, content, lines))
                
                if self.config.get('check_for_insecure_defaults', True):
                    findings.extend(self.check_insecure_defaults(file_path, content, lines))
                    findings.extend(self.check_logging_exposure(file_path, content, lines))
                
                findings.extend(self.check_exposed_config_files(file_path))
                
        except PermissionError:
            logger.warning(f"Permission denied: {file_path}")
        except Exception as e:
            logger.error(f"Error reviewing {file_path}: {str(e)}")
        
        return findings

    def review(self, path: str = '.') -> List[Dict]:
        if not self.validate_inputs(path):
            return self.findings

        logger.info(f"Starting configuration review on {path}")

        p = Path(path)
        total_files = 0

        for file_path in p.rglob('*'):
            if not file_path.is_file():
                continue
            
            if file_path.suffix.lower() not in self.config.get('file_extensions', []):
                continue
            
            if any(pattern in str(file_path) for pattern in self.config.get('exclude_patterns', [])):
                continue

            findings = self.review_file(file_path)
            self.findings.extend(findings)
            total_files += 1

        logger.info(f"Reviewed {total_files} files, found {len(self.findings)} issues")
        return self.findings

    def generate_report(self, output_format: str = 'json') -> str:
        import json
        if output_format == 'json':
            return json.dumps(self.findings, indent=2)
        elif output_format == 'text':
            report = []
            for finding in self.findings:
                report.append(f"\n{finding['file']}:{finding['line']}")
                report.append(f"  Issue: {finding['issue']}")
                report.append(f"  Severity: {finding['severity'].upper()}")
                report.append(f"  Context: {finding.get('context', 'N/A')}")
                report.append(f"  Recommendation: {finding['recommendation']}")
            return "\n".join(report)
        return json.dumps(self.findings, indent=2)

def main():
    parser = argparse.ArgumentParser(description='Security Configuration Reviewer')
    parser.add_argument('path', nargs='?', default='.', help='Path to review')
    parser.add_argument('--config', help='Configuration file path (YAML/JSON)')
    parser.add_argument('--format', choices=['json', 'text'], default='json',
                        help='Output format')
    parser.add_argument('--output', help='Output file path')

    args = parser.parse_args()

    reviewer = ConfigReviewer(args.config)
    results = reviewer.review(args.path)
    report = reviewer.generate_report(args.format)

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
        logger.info("No configuration issues found")
        sys.exit(0)

if __name__ == '__main__':
    main()
