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

class ThreatModeler:
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.threats = []

    def _load_config(self, config_path: Optional[str]) -> Dict:
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        return {
            'methodology': 'STRIDE',
            'scope': '.',
            'assets': []
        }

    def validate_inputs(self, path: str) -> bool:
        if not Path(path).exists():
            logger.error(f"Path does not exist: {path}")
            return False
        return True

    def analyze_stride_threats(self, component: str) -> List[Dict]:
        threats = []
        
        stride_threats = {
            'Spoofing': {
                'description': 'Impersonation of something or someone',
                'mitigations': [
                    'Strong authentication',
                    'Multi-factor authentication',
                    'Certificate-based auth'
                ],
                'severity': 'high'
            },
            'Tampering': {
                'description': 'Modification of data or code',
                'mitigations': [
                    'Digital signatures',
                    'Hash verification',
                    'Access controls'
                ],
                'severity': 'high'
            },
            'Repudiation': {
                'description': 'Refusal to perform an action',
                'mitigations': [
                    'Audit logging',
                    'Non-repudiation services',
                    'Digital signatures'
                ],
                'severity': 'medium'
            },
            'Information Disclosure': {
                'description': 'Exposure of information to unauthorized parties',
                'mitigations': [
                    'Encryption',
                    'Access controls',
                    'Secure data handling'
                ],
                'severity': 'high'
            },
            'Denial of Service': {
                'description': 'Denial of service or access',
                'mitigations': [
                    'Rate limiting',
                    'Redundancy',
                    'Throttling'
                ],
                'severity': 'medium'
            },
            'Elevation of Privilege': {
                'description': 'Gain higher privileges than authorized',
                'mitigations': [
                    'Principle of least privilege',
                    'Secure session management',
                    'Input validation'
                ],
                'severity': 'high'
            }
        }
        
        for threat_type, details in stride_threats.items():
            threats.append({
                'component': component,
                'threat_type': threat_type,
                'description': details['description'],
                'mitigations': details['mitigations'],
                'severity': details['severity']
            })
        
        return threats

    def identify_assets(self, path: str) -> List[str]:
        assets = []
        
        p = Path(path)
        
        for file_path in p.rglob('*'):
            if not file_path.is_file():
                continue
            
            if file_path.suffix in ['.py', '.js', '.ts', '.java', '.go']:
                assets.append(str(file_path))
        
        config_files = ['config.yaml', 'config.json', 'config.py', '.env']
        for config in config_files:
            if (p / config).exists():
                assets.append(str(p / config))
        
        return assets

    def calculate_risk(self, threat: Dict) -> float:
        likelihood = threat.get('likelihood', 'medium')
        impact = threat.get('impact', 'medium')
        
        likelihood_scores = {'low': 1, 'medium': 2, 'high': 3}
        impact_scores = {'low': 1, 'medium': 2, 'high': 3}
        
        score = likelihood_scores.get(likelihood, 2) * impact_scores.get(impact, 2)
        return score

    def model_threats(self, path: str = '.') -> List[Dict]:
        if not self.validate_inputs(path):
            return self.threats

        logger.info(f"Starting threat modeling on {path}")

        assets = self.identify_assets(path)
        
        for asset in assets:
            threats = self.analyze_stride_threats(asset)
            self.threats.extend(threats)

        logger.info(f"Threat modeling completed. Identified {len(self.threats)} potential threats")
        return self.threats

    def generate_report(self, output_format: str = 'json') -> str:
        if output_format == 'json':
            return json.dumps(self.threats, indent=2)
        elif output_format == 'text':
            report = []
            for threat in self.threats:
                report.append(f"\nComponent: {threat['component']}")
                report.append(f"Threat Type: {threat['threat_type']}")
                report.append(f"Severity: {threat['severity']}")
                report.append(f"Description: {threat['description']}")
                report.append(f"Mitigations:")
                for mitigation in threat['mitigations']:
                    report.append(f"  - {mitigation}")
            return "\n".join(report)
        return json.dumps(self.threats, indent=2)

def main():
    parser = argparse.ArgumentParser(description='Threat Modeling Analysis')
    parser.add_argument('path', nargs='?', default='.', help='Path to model')
    parser.add_argument('--config', help='Configuration file path (YAML/JSON)')
    parser.add_argument('--format', choices=['json', 'text'], default='json',
                        help='Output format')
    parser.add_argument('--output', help='Output file path')

    args = parser.parse_args()

    modeler = ThreatModeler(args.config)
    results = modeler.model_threats(args.path)
    report = modeler.generate_report(args.format)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        logger.info(f"Report saved to {args.output}")
    else:
        print(report)

    logger.info("Threat modeling completed")
    sys.exit(0)

if __name__ == '__main__':
    main()
