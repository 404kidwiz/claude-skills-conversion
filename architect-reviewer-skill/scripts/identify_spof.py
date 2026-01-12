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

class SinglePointOfFailureIdentifier:
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.spofs = []

    def _load_config(self, config_path: Optional[str]) -> Dict:
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        return {
            'check_dependencies': True,
            'check_infrastructure': True,
            'check_services': True
        }

    def validate_inputs(self, path: str) -> bool:
        if not Path(path).exists():
            logger.error(f"Path does not exist: {path}")
            return False
        return True

    def identify_dependency_spofs(self, path: str) -> List[Dict]:
        spofs = []
        
        try:
            if Path('requirements.txt').exists():
                with open('requirements.txt', 'r') as f:
                    deps = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                
                if len(deps) < 5:
                    spofs.append({
                        'type': 'dependency',
                        'category': 'low_count',
                        'severity': 'low',
                        'description': 'Few dependencies (potentially okay)',
                        'recommendation': 'Review dependencies for necessity'
                    })
            
            if Path('package.json').exists():
                with open('package.json', 'r') as f:
                    pkg_data = json.load(f)
                    deps = pkg_data.get('dependencies', {})
                    
                    critical_deps = ['express', 'react', 'angular', 'vue']
                    for dep in critical_deps:
                        if dep in deps:
                            spofs.append({
                                'type': 'dependency',
                                'category': 'critical_dependency',
                                'severity': 'medium',
                                'dependency': dep,
                                'description': f'Dependency on {dep} - consider alternatives',
                                'recommendation': 'Evaluate if alternative libraries could reduce dependency'
                            })
        except Exception as e:
            logger.error(f"Error analyzing dependencies: {str(e)}")
        
        return spofs

    def identify_infrastructure_spofs(self, path: str) -> List[Dict]:
        spofs = []
        
        for file_path in Path(path).rglob('*.tf'):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                if 'count = 1' in content or 'count = 0' in content:
                    spofs.append({
                        'type': 'infrastructure',
                        'file': str(file_path),
                        'category': 'single_instance',
                        'severity': 'high',
                        'description': 'Single resource instance (potential SPOF)',
                        'recommendation': 'Consider high availability with multiple instances'
                    })
            except:
                pass
        
        return spofs

    def identify_service_spofs(self, path: str) -> List[Dict]:
        spofs = []
        
        for file_path in Path(path).rglob('docker-compose.yml'):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                if 'restart: on-failure' not in content:
                    spofs.append({
                        'type': 'service',
                        'file': str(file_path),
                        'category': 'no_restart_policy',
                        'severity': 'medium',
                        'description': 'Service without restart policy',
                        'recommendation': 'Add restart policy for better reliability'
                    })
                
                if 'depends_on' in content:
                    spofs.append({
                        'type': 'service',
                        'file': str(file_path),
                        'category': 'service_dependency',
                        'severity': 'medium',
                        'description': 'Service dependencies detected',
                        'recommendation': 'Review dependencies for SPOF risk'
                    })
            except:
                pass
        
        return spofs

    def identify(self, path: str = '.') -> List[Dict]:
        if not self.validate_inputs(path):
            return self.spofs

        logger.info(f"Starting SPOF identification on {path}")

        if self.config.get('check_dependencies', True):
            self.spofs.extend(self.identify_dependency_spofs(path))
        
        if self.config.get('check_infrastructure', True):
            self.spofs.extend(self.identify_infrastructure_spofs(path))
        
        if self.config.get('check_services', True):
            self.spofs.extend(self.identify_service_spofs(path))

        logger.info(f"SPOF identification completed. Found {len(self.spofs)} potential SPOFs")
        return self.spofs

    def generate_report(self, output_format: str = 'json') -> str:
        if output_format == 'json':
            return json.dumps(self.spofs, indent=2)
        elif output_format == 'text':
            report = []
            for spof in self.spofs:
                report.append(f"\nType: {spof['type']}")
                report.append(f"Category: {spof['category']}")
                report.append(f"Severity: {spof['severity']}")
                report.append(f"Description: {spof['description']}")
                report.append(f"Recommendation: {spof['recommendation']}")
            return "\n".join(report)
        return json.dumps(self.spofs, indent=2)

def main():
    parser = argparse.ArgumentParser(description='Single Point of Failure Identification')
    parser.add_argument('path', nargs='?', default='.', help='Path to analyze')
    parser.add_argument('--config', help='Configuration file path (YAML/JSON)')
    parser.add_argument('--format', choices=['json', 'text'], default='json',
                        help='Output format')
    parser.add_argument('--output', help='Output file path')

    args = parser.parse_args()

    identifier = SinglePointOfFailureIdentifier(args.config)
    results = identifier.identify(args.path)
    report = identifier.generate_report(args.format)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        logger.info(f"Report saved to {args.output}")
    else:
        print(report)

    logger.info("SPOF identification completed")
    sys.exit(0)

if __name__ == '__main__':
    main()
