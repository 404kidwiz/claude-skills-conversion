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

class SQLInjectionTester:
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.vulnerabilities = []

    def _load_config(self, config_path: Optional[str]) -> Dict:
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        return {
            'target_url': '',
            'test_level': 3,
            'risk_level': 2,
            'batch_mode': True
        }

    def validate_inputs(self, target_url: str) -> bool:
        if not target_url.startswith(('http://', 'https://')):
            logger.error(f"Invalid URL: {target_url}")
            return False
        return True

    def run_sqlmap(self, target_url: str) -> List[Dict]:
        findings = []
        
        try:
            logger.info(f"Running SQLMap on {target_url}")
            logger.warning("WARNING: Only test applications you own or have authorization to test")
            
            sqlmap_options = [
                '-u', target_url,
                '--batch',
                '--level', str(self.config.get('test_level', 3)),
                '--risk', str(self.config.get('risk_level', 2)),
                '--dbs'
            ]
            
            result = subprocess.run(
                ['sqlmap'] + sqlmap_options,
                capture_output=True,
                text=True,
                timeout=1800
            )
            
            findings.append({
                'tool': 'sqlmap',
                'target': target_url,
                'status': 'completed' if result.returncode == 0 else 'failed',
                'output_length': len(result.stdout)
            })
            
            logger.info("SQLMap scan completed. Review output for SQL injection vulnerabilities")
            
        except FileNotFoundError:
            logger.warning("SQLMap not found. Install: https://sqlmap.org/")
        except subprocess.TimeoutExpired:
            logger.error("SQLMap scan timed out")
        except Exception as e:
            logger.error(f"Error running SQLMap: {str(e)}")

        return findings

    def scan(self, target_url: str) -> List[Dict]:
        if not self.validate_inputs(target_url):
            return self.vulnerabilities

        logger.info(f"Starting SQL injection test on {target_url}")
        self.vulnerabilities.extend(self.run_sqlmap(target_url))
        
        logger.info(f"SQL injection test completed for {target_url}")
        return self.vulnerabilities

    def generate_report(self) -> str:
        import json
        return json.dumps(self.vulnerabilities, indent=2)

def main():
    parser = argparse.ArgumentParser(description='SQL Injection Tester')
    parser.add_argument('url', help='Target URL')
    parser.add_argument('--config', help='Configuration file path (YAML/JSON)')
    parser.add_argument('--output', help='Output file path')

    args = parser.parse_args()

    tester = SQLInjectionTester(args.config)
    results = tester.scan(args.url)
    report = tester.generate_report()

    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        logger.info(f"Report saved to {args.output}")
    else:
        print(report)

    logger.info("SQL injection test completed")
    sys.exit(0)

if __name__ == '__main__':
    main()
