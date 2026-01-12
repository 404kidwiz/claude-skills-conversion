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

class ReconScanner:
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.recon_data = {}

    def _load_config(self, config_path: Optional[str]) -> Dict:
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        return {
            'target_domains': [],
            'wordlist': '/usr/share/wordlists/dirb/common.txt',
            'max_threads': 50,
            'scan_depth': 3
        }

    def validate_inputs(self, target: str) -> bool:
        if not target or '.' not in target:
            logger.error(f"Invalid target: {target}")
            return False
        return True

    def dns_enumeration(self, target: str) -> Dict:
        results = {'subdomains': [], 'dns_records': {}}
        
        try:
            logger.info(f"Performing DNS enumeration on {target}")
            
            result = subprocess.run(
                ['sublist3r', '-d', target, '-o', f'{target}_subdomains.txt'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if Path(f'{target}_subdomains.txt').exists():
                with open(f'{target}_subdomains.txt', 'r') as f:
                    subdomains = [line.strip() for line in f if line.strip()]
                results['subdomains'] = subdomains
            
            result = subprocess.run(
                ['dig', '+short', 'ANY', target],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.stdout:
                results['dns_records']['any'] = result.stdout.strip().split('\n')
                
        except FileNotFoundError:
            logger.warning("sublist3r not found. Install: pip install sublist3r")
        except subprocess.TimeoutExpired:
            logger.error("DNS enumeration timed out")
        except Exception as e:
            logger.error(f"Error in DNS enumeration: {str(e)}")

        return results

    def port_scan(self, target: str) -> Dict:
        results = {'open_ports': [], 'services': {}}
        
        try:
            logger.info(f"Scanning ports on {target}")
            result = subprocess.run(
                ['nmap', '-sV', '-sC', '-p-', '-T4', '--max-rate', '1000', 
                 '-oX', f'{target}_nmap.xml', target],
                capture_output=True,
                text=True,
                timeout=1800
            )
            
            if result.returncode == 0:
                results['scan_successful'] = True
                
        except FileNotFoundError:
            logger.warning("nmap not found. Install: sudo apt install nmap")
        except subprocess.TimeoutExpired:
            logger.error("Port scan timed out")
        except Exception as e:
            logger.error(f"Error in port scan: {str(e)}")

        return results

    def web_crawling(self, target: str) -> Dict:
        results = {'endpoints': [], 'forms': [], 'comments': []}
        
        try:
            logger.info(f"Crawling {target}")
            result = subprocess.run(
                ['nikto', '-h', target, '-C', 'all', '-output', f'{target}_nikto.txt'],
                capture_output=True,
                text=True,
                timeout=600
            )
            
            results['nikto_scan'] = result.returncode == 0
            
        except FileNotFoundError:
            logger.warning("nikto not found. Install: sudo apt install nikto")
        except subprocess.TimeoutExpired:
            logger.error("Web crawling timed out")
        except Exception as e:
            logger.error(f"Error in web crawling: {str(e)}")

        return results

    def technology_detection(self, target: str) -> Dict:
        results = {'technologies': []}
        
        try:
            logger.info(f"Detecting technologies on {target}")
            result = subprocess.run(
                ['whatweb', target, '--log-json', f'{target}_whatweb.json'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if Path(f'{target}_whatweb.json').exists():
                with open(f'{target}_whatweb.json', 'r') as f:
                    tech_data = json.load(f)
                results['technologies'] = tech_data[0].get('plugins', {}).keys()
                
        except FileNotFoundError:
            logger.warning("whatweb not found. Install: sudo apt install whatweb")
        except subprocess.TimeoutExpired:
            logger.error("Technology detection timed out")
        except Exception as e:
            logger.error(f"Error in technology detection: {str(e)}")

        return results

    def directory_brute_force(self, target: str) -> Dict:
        results = {'directories': [], 'files': []}
        
        try:
            logger.info(f"Brute-forcing directories on {target}")
            result = subprocess.run(
                ['gobuster', 'dir', '-u', f'http://{target}', '-w', 
                 self.config.get('wordlist', '/usr/share/wordlists/dirb/common.txt'),
                 '-t', str(self.config.get('max_threads', 50)),
                 '-o', f'{target}_gobuster.txt'],
                capture_output=True,
                text=True,
                timeout=600
            )
            
            results['scan_completed'] = result.returncode == 0
            
        except FileNotFoundError:
            logger.warning("gobuster not found. Install: sudo apt install gobuster")
        except subprocess.TimeoutExpired:
            logger.error("Directory brute force timed out")
        except Exception as e:
            logger.error(f"Error in directory brute force: {str(e)}")

        return results

    def scan(self, target: str) -> Dict:
        if not self.validate_inputs(target):
            return self.recon_data

        logger.info(f"Starting reconnaissance on {target}")
        logger.warning("WARNING: Only scan targets you own or have authorization to test")

        self.recon_data = {
            'target': target,
            'timestamp': subprocess.run(['date'], capture_output=True, text=True).stdout.strip()
        }
        
        self.recon_data.update(self.dns_enumeration(target))
        self.recon_data.update(self.port_scan(target))
        self.recon_data.update(self.web_crawling(target))
        self.recon_data.update(self.technology_detection(target))
        self.recon_data.update(self.directory_brute_force(target))

        logger.info(f"Reconnaissance completed for {target}")
        return self.recon_data

    def generate_report(self, output_format: str = 'json') -> str:
        if output_format == 'json':
            return json.dumps(self.recon_data, indent=2)
        elif output_format == 'text':
            report = []
            report.append(f"Target: {self.recon_data.get('target', 'unknown')}")
            report.append(f"Timestamp: {self.recon_data.get('timestamp', 'unknown')}")
            
            if self.recon_data.get('subdomains'):
                report.append(f"\nSubdomains found: {len(self.recon_data['subdomains'])}")
                for sub in self.recon_data['subdomains'][:10]:
                    report.append(f"  - {sub}")
            
            if self.recon_data.get('technologies'):
                report.append(f"\nTechnologies detected: {len(self.recon_data['technologies'])}")
                for tech in self.recon_data['technologies']:
                    report.append(f"  - {tech}")
            
            return "\n".join(report)
        return json.dumps(self.recon_data, indent=2)

def main():
    parser = argparse.ArgumentParser(description='Penetration Testing Reconnaissance Scanner')
    parser.add_argument('target', help='Target domain or IP')
    parser.add_argument('--config', help='Configuration file path (YAML/JSON)')
    parser.add_argument('--format', choices=['json', 'text'], default='json',
                        help='Output format')
    parser.add_argument('--output', help='Output file path')

    args = parser.parse_args()

    scanner = ReconScanner(args.config)
    results = scanner.scan(args.target)
    report = scanner.generate_report(args.format)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        logger.info(f"Report saved to {args.output}")
    else:
        print(report)

    logger.info("Reconnaissance scan completed")
    sys.exit(0)

if __name__ == '__main__':
    main()
