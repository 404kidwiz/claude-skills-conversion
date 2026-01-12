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

class SecurityDesignReviewer:
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.findings = []

    def _load_config(self, config_path: Optional[str]) -> Dict:
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        return {
            'check_auth': True,
            'check_encryption': True,
            'check_input_validation': True,
            'check_authorization': True
        }

    def validate_inputs(self, path: str) -> bool:
        if not Path(path).exists():
            logger.error(f"Path does not exist: {path}")
            return False
        return True

    def review_authentication_design(self, path: str) -> List[Dict]:
        findings = []
        
        auth_patterns = [
            'password_hash',
            'salt',
            'bcrypt',
            'argon2',
            'mfa',
            'oauth2',
            'jwt',
            'session'
        ]
        
        for file_path in Path(path).rglob('*.py'):
            if not file_path.is_file():
                continue
            
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                has_password_storage = any(p in content.lower() for p in ['password', 'passwd'])
                has_hashing = any(h in content.lower() for h in ['bcrypt', 'argon2', 'pbkdf2'])
                has_mfa = any(m in content.lower() for m in ['mfa', 'totp', '2fa'])
                
                if has_password_storage and not has_hashing:
                    findings.append({
                        'file': str(file_path),
                        'category': 'authentication',
                        'issue': 'plaintext_password_storage',
                        'severity': 'high',
                        'description': 'Password storage detected without secure hashing',
                        'recommendation': 'Use bcrypt, argon2, or scrypt for password hashing'
                    })
                
                if has_password_storage and not has_mfa:
                    findings.append({
                        'file': str(file_path),
                        'category': 'authentication',
                        'issue': 'no_mfa',
                        'severity': 'medium',
                        'description': 'No multi-factor authentication detected',
                        'recommendation': 'Implement MFA for sensitive operations'
                    })
            except:
                pass
        
        return findings

    def review_encryption_design(self, path: str) -> List[Dict]:
        findings = []
        
        encryption_keywords = ['encrypt', 'decrypt', 'cipher', 'aes', 'rsa']
        weak_algorithms = ['des', 'md5', 'sha1', 'rc4']
        
        for file_path in Path(path).rglob('*'):
            if not file_path.is_file():
                continue
            
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                has_weak_crypto = any(w in content.lower() for w in weak_algorithms)
                has_encryption = any(e in content.lower() for e in encryption_keywords)
                
                if has_encryption and has_weak_crypto:
                    findings.append({
                        'file': str(file_path),
                        'category': 'encryption',
                        'issue': 'weak_encryption',
                        'severity': 'high',
                        'description': 'Weak encryption algorithm detected',
                        'recommendation': 'Use AES-256, SHA-256, or stronger algorithms'
                    })
            except:
                pass
        
        return findings

    def review_input_validation(self, path: str) -> List[Dict]:
        findings = []
        
        for file_path in Path(path).rglob('*.py'):
            if not file_path.is_file():
                continue
            
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                has_user_input = 'request.' in content or 'input(' in content
                has_validation = any(v in content.lower() for v in ['validate', 'sanitize', 'escape'])
                
                if has_user_input and not has_validation:
                    findings.append({
                        'file': str(file_path),
                        'category': 'input_validation',
                        'issue': 'missing_input_validation',
                        'severity': 'high',
                        'description': 'User input without validation',
                        'recommendation': 'Validate and sanitize all user input'
                    })
            except:
                pass
        
        return findings

    def review(self, path: str = '.') -> List[Dict]:
        if not self.validate_inputs(path):
            return self.findings

        logger.info(f"Starting security design review on {path}")

        if self.config.get('check_auth', True):
            self.findings.extend(self.review_authentication_design(path))
        
        if self.config.get('check_encryption', True):
            self.findings.extend(self.review_encryption_design(path))
        
        if self.config.get('check_input_validation', True):
            self.findings.extend(self.review_input_validation(path))

        logger.info(f"Security design review completed. Found {len(self.findings)} issues")
        return self.findings

    def generate_report(self, output_format: str = 'json') -> str:
        if output_format == 'json':
            return json.dumps(self.findings, indent=2)
        elif output_format == 'text':
            report = []
            for finding in self.findings:
                report.append(f"\n{finding['file']}")
                report.append(f"  Category: {finding['category']}")
                report.append(f"  Severity: {finding['severity']}")
                report.append(f"  Issue: {finding['issue']}")
                report.append(f"  Description: {finding['description']}")
                report.append(f"  Recommendation: {finding['recommendation']}")
            return "\n".join(report)
        return json.dumps(self.findings, indent=2)

def main():
    parser = argparse.ArgumentParser(description='Security Design Review')
    parser.add_argument('path', nargs='?', default='.', help='Path to review')
    parser.add_argument('--config', help='Configuration file path (YAML/JSON)')
    parser.add_argument('--format', choices=['json', 'text'], default='json',
                        help='Output format')
    parser.add_argument('--output', help='Output file path')

    args = parser.parse_args()

    reviewer = SecurityDesignReviewer(args.config)
    results = reviewer.review(args.path)
    report = reviewer.generate_report(args.format)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        logger.info(f"Report saved to {args.output}")
    else:
        print(report)

    logger.info("Security design review completed")
    sys.exit(0)

if __name__ == '__main__':
    main()
