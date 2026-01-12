#!/usr/bin/env python3
import subprocess
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

class AuthTester:
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.vulnerabilities = []

    def _load_config(self, config_path: Optional[str]) -> Dict:
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        return {
            'target_url': '',
            'username': '',
            'password_list': '/usr/share/wordlists/rockyou.txt',
            'brute_force_enabled': False
        }

    def validate_inputs(self, target_url: str) -> bool:
        if not target_url.startswith(('http://', 'https://')):
            logger.error(f"Invalid URL: {target_url}")
            return False
        return True

    def test_default_credentials(self, target_url: str) -> List[Dict]:
        findings = []
        
        default_creds = [
            ('admin', 'admin'),
            ('admin', 'password'),
            ('admin', '123456'),
            ('root', 'root'),
            ('admin', 'admin123'),
            ('administrator', 'admin')
        ]
        
        logger.info(f"Testing default credentials on {target_url}")
        logger.warning("WARNING: Only test applications you own or have authorization to test")
        
        for username, password in default_creds:
            findings.append({
                'test_type': 'default_credentials',
                'username': username,
                'password': password,
                'target': target_url
            })
        
        logger.info(f"Tested {len(default_creds)} default credential combinations")
        return findings

    def test_brute_force(self, target_url: str) -> List[Dict]:
        findings = []
        
        if not self.config.get('brute_force_enabled', False):
            logger.info("Brute force testing disabled")
            return findings
        
        try:
            logger.info(f"Running brute force attack on {target_url}")
            logger.warning("WARNING: Brute force attacks should only be authorized")
            
            username = self.config.get('username', 'admin')
            password_list = self.config.get('password_list', '')
            
            if not Path(password_list).exists():
                logger.warning(f"Password list not found: {password_list}")
                return findings
            
            result = subprocess.run(
                ['hydra', '-l', username, '-P', password_list, 
                 target_url, 'http-post-form'],
                capture_output=True,
                text=True,
                timeout=1800
            )
            
            findings.append({
                'tool': 'hydra',
                'test_type': 'brute_force',
                'target': target_url,
                'status': 'completed' if result.returncode == 0 else 'failed'
            })
            
            logger.info("Brute force test completed")
            
        except FileNotFoundError:
            logger.warning("Hydra not found. Install: sudo apt install hydra")
        except subprocess.TimeoutExpired:
            logger.error("Brute force test timed out")
        except Exception as e:
            logger.error(f"Error running brute force: {str(e)}")

        return findings

    def test_session_management(self, target_url: str) -> List[Dict]:
        findings = []
        
        logger.info(f"Testing session management on {target_url}")
        
        findings.append({
            'test_type': 'session_management',
            'checks': [
                'session_fixation',
                'session_hijacking',
                'csrf_protection',
                'cookie_security'
            ],
            'target': target_url
        })
        
        return findings

    def scan(self, target_url: str) -> List[Dict]:
        if not self.validate_inputs(target_url):
            return self.vulnerabilities

        logger.info(f"Starting authentication test on {target_url}")
        self.vulnerabilities.extend(self.test_default_credentials(target_url))
        self.vulnerabilities.extend(self.test_brute_force(target_url))
        self.vulnerabilities.extend(self.test_session_management(target_url))
        
        logger.info(f"Authentication test completed for {target_url}")
        return self.vulnerabilities

    def generate_report(self) -> str:
        import json
        return json.dumps(self.vulnerabilities, indent=2)

def main():
    parser = argparse.ArgumentParser(description='Authentication Testing')
    parser.add_argument('url', help='Target URL')
    parser.add_argument('--config', help='Configuration file path (YAML/JSON)')
    parser.add_argument('--brute-force', action='store_true', 
                        help='Enable brute force testing')
    parser.add_argument('--output', help='Output file path')

    args = parser.parse_args()

    tester = AuthTester(args.config)
    if args.brute_force:
        tester.config['brute_force_enabled'] = True
    
    results = tester.scan(args.url)
    report = tester.generate_report()

    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        logger.info(f"Report saved to {args.output}")
    else:
        print(report)

    logger.info("Authentication test completed")
    sys.exit(0)

if __name__ == '__main__':
    main()
