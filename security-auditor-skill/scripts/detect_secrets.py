#!/usr/bin/env python3
import re
import sys
import logging
import json
from pathlib import Path
from typing import List, Dict, Optional
import argparse
import hashlib

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SecretDetector:
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.patterns = self._load_patterns()
        self.findings = []

    def _load_config(self, config_path: Optional[str]) -> Dict:
        if config_path and Path(config_path).exists():
            import yaml
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        return {
            'scan_paths': ['.'],
            'exclude_patterns': ['venv', '__pycache__', '.git', 'node_modules'],
            'file_extensions': ['.py', '.js', '.ts', '.java', '.go', '.rb', '.php', '.sh', '.yml', '.yaml', '.json', '.env', '.config'],
            'max_file_size_mb': 10
        }

    def _load_patterns(self) -> Dict[str, str]:
        return {
            'api_key': r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?',
            'aws_access_key': r'(?i)aws[_-]?(access[_-]?key[_-]?id)\s*[:=]\s*["\']?(AKIA[0-9A-Z]{16})["\']?',
            'aws_secret_key': r'(?i)aws[_-]?(secret[_-]?(access[_-]?key)?)\s*[:=]\s*["\']?([0-9a-zA-Z/+]{40})["\']?',
            'private_key': r'-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----',
            'github_token': r'(?i)github[_-]?token\s*[:=]\s*["\']?(gh[pousr]_[a-zA-Z0-9]{36,255})["\']?',
            'password': r'(?i)(password|passwd|pwd)\s*[:=]\s*["\']?([^"\s\'\)]{8,})["\']?',
            'database_url': r'(?i)(database[_-]?url|db[_-]?url)\s*[:=]\s*["\']?(postgres://|mysql://|mongodb://|sqlite://)[^\s"\']{10,}["\']?',
            'jwt_secret': r'(?i)(jwt[_-]?(secret|key)|secret[_-]?key)\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{32,})["\']?',
            'slack_token': r'(?i)slack[_-]?token\s*[:=]\s*["\']?(xox[baprs]-[a-zA-Z0-9\-]{10,200})["\']?',
            'bearer_token': r'(?i)bearer\s+([a-zA-Z0-9_\-\.]{20,})',
            'oauth_token': r'(?i)oauth[_-]?token\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?',
            'stripe_key': r'(?i)stripe[_-]?(secret[_-]?key|public[_-]?key)\s*[:=]\s*["\']?(sk_live_|pk_live_)[a-zA-Z0-9]{20,}["\']?',
            'heroku_api_key': r'(?i)heroku[_-]?api[_-]?key\s*[:=]\s*["\']?([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})["\']?',
        }

    def validate_inputs(self, scan_path: str) -> bool:
        if not Path(scan_path).exists():
            logger.error(f"Path does not exist: {scan_path}")
            return False
        return True

    def mask_secret(self, secret: str, show_chars: int = 4) -> str:
        if len(secret) <= show_chars:
            return '*' * len(secret)
        return secret[:show_chars] + '*' * (len(secret) - show_chars * 2) + secret[-show_chars:]

    def scan_file(self, file_path: Path) -> List[Dict]:
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
                for pattern_name, pattern in self.patterns.items():
                    for line_num, line in enumerate(lines, 1):
                        matches = re.finditer(pattern, line)
                        for match in matches:
                            secret_value = match.group(2) if match.lastindex >= 2 else match.group(0)
                            findings.append({
                                'file': str(file_path),
                                'line': line_num,
                                'pattern': pattern_name,
                                'secret': self.mask_secret(secret_value),
                                'secret_hash': hashlib.sha256(secret_value.encode()).hexdigest()[:16],
                                'context': line.strip()[:100]
                            })
        except PermissionError:
            logger.warning(f"Permission denied: {file_path}")
        except Exception as e:
            logger.error(f"Error scanning {file_path}: {str(e)}")
        
        return findings

    def scan_directory(self, scan_path: str = '.') -> List[Dict]:
        if not self.validate_inputs(scan_path):
            return self.findings

        logger.info(f"Starting secret detection scan on {scan_path}")

        path = Path(scan_path)
        total_files = 0

        for file_path in path.rglob('*'):
            if not file_path.is_file():
                continue
            
            if file_path.suffix.lower() not in self.config.get('file_extensions', []):
                continue
            
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            if file_size_mb > self.config.get('max_file_size_mb', 10):
                logger.debug(f"Skipping large file: {file_path} ({file_size_mb:.2f}MB)")
                continue

            if any(pattern in str(file_path) for pattern in self.config.get('exclude_patterns', [])):
                continue

            findings = self.scan_file(file_path)
            self.findings.extend(findings)
            total_files += 1

        logger.info(f"Scanned {total_files} files, found {len(self.findings)} potential secrets")
        return self.findings

    def generate_report(self, output_format: str = 'json') -> str:
        if output_format == 'json':
            return json.dumps(self.findings, indent=2)
        elif output_format == 'text':
            report = []
            for finding in self.findings:
                report.append(f"\n{finding['file']}:{finding['line']}")
                report.append(f"  Pattern: {finding['pattern']}")
                report.append(f"  Secret (masked): {finding['secret']}")
                report.append(f"  Context: {finding['context']}")
            return "\n".join(report)
        return json.dumps(self.findings, indent=2)

def main():
    parser = argparse.ArgumentParser(description='Secret Detection Scanner')
    parser.add_argument('path', nargs='?', default='.', help='Path to scan')
    parser.add_argument('--config', help='Configuration file path (YAML/JSON)')
    parser.add_argument('--format', choices=['json', 'text'], default='json',
                        help='Output format')
    parser.add_argument('--output', help='Output file path')

    args = parser.parse_args()

    detector = SecretDetector(args.config)
    results = detector.scan_directory(args.path)
    report = detector.generate_report(args.format)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        logger.info(f"Report saved to {args.output}")
    else:
        print(report)

    if len(results) > 0:
        logger.error(f"Found {len(results)} potential secrets")
        sys.exit(1)
    else:
        logger.info("No secrets found")
        sys.exit(0)

if __name__ == '__main__':
    main()
