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

class XSSTester:
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.vulnerabilities = []

    def _load_config(self, config_path: Optional[str]) -> Dict:
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        return {
            'target_url': '',
            'xss_payloads': ['<script>alert(1)</script>', '<img src=x onerror=alert(1)>'],
            'crawl': True
        }

    def validate_inputs(self, target_url: str) -> bool:
        if not target_url.startswith(('http://', 'https://')):
            logger.error(f"Invalid URL: {target_url}")
            return False
        return True

    def run_xsser(self, target_url: str) -> List[Dict]:
        findings = []
        
        try:
            logger.info(f"Running XSSer on {target_url}")
            logger.warning("WARNING: Only test applications you own or have authorization to test")
            
            xsser_options = ['--url', target_url, '--auto']
            
            if self.config.get('crawl', True):
                xsser_options.append('--crawl')
            
            result = subprocess.run(
                ['xsser'] + xsser_options,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            findings.append({
                'tool': 'xsser',
                'target': target_url,
                'status': 'completed' if result.returncode == 0 else 'failed'
            })
            
            logger.info("XSSer scan completed")
            
        except FileNotFoundError:
            logger.warning("XSSer not found. Install: sudo apt install xsser")
        except subprocess.TimeoutExpired:
            logger.error("XSSer scan timed out")
        except Exception as e:
            logger.error(f"Error running XSSer: {str(e)}")

        return findings

    def run_xss_strike(self, target_url: str) -> List[Dict]:
        findings = []
        
        try:
            logger.info(f"XSStrike requires manual execution")
            logger.info("Download: https://github.com/s0md3v/XSStrike")
            
        except Exception as e:
            logger.error(f"Error with XSStrike: {str(e)}")

        return findings

    def scan(self, target_url: str) -> List[Dict]:
        if not self.validate_inputs(target_url):
            return self.vulnerabilities

        logger.info(f"Starting XSS test on {target_url}")
        self.vulnerabilities.extend(self.run_xsser(target_url))
        self.vulnerabilities.extend(self.run_xss_strike(target_url))
        
        logger.info(f"XSS test completed for {target_url}")
        return self.vulnerabilities

    def generate_report(self) -> str:
        import json
        return json.dumps(self.vulnerabilities, indent=2)

def main():
    parser = argparse.ArgumentParser(description='XSS/CSRF Tester')
    parser.add_argument('url', help='Target URL')
    parser.add_argument('--config', help='Configuration file path (YAML/JSON)')
    parser.add_argument('--output', help='Output file path')

    args = parser.parse_args()

    tester = XSSTester(args.config)
    results = tester.scan(args.url)
    report = tester.generate_report()

    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        logger.info(f"Report saved to {args.output}")
    else:
        print(report)

    logger.info("XSS test completed")
    sys.exit(0)

if __name__ == '__main__':
    main()
