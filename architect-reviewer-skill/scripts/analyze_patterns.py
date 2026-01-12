# Architecture Patterns Analysis Script

#!/usr/bin/env python3
import subprocess
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
import argparse
import yaml
import ast

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ArchitectureAnalyzer:
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.patterns = self._load_patterns()
        self.analysis_results = {}

    def _load_config(self, config_path: Optional[str]) -> Dict:
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        return {
            'project_root': '.',
            'file_patterns': ['*.py', '*.js', '*.java', '*.go', '*.ts'],
            'check_for': [
                'microservices',
                'monolith',
                'event_driven',
                'layered',
                'hexagonal'
            ]
        }

    def _load_patterns(self) -> Dict:
        return {
            'microservices': [
                'service_discovery',
                'api_gateway',
                'message_queue',
                'kafka',
                'rabbitmq'
            ],
            'monolith': [
                'single_database',
                'shared_state',
                'coupled_modules',
                'shared_libs'
            ],
            'event_driven': [
                'event_bus',
                'publisher',
                'subscriber',
                'event_store',
                'cqrs'
            ],
            'layered': [
                'controller',
                'service_layer',
                'repository',
                'dto'
            ],
            'hexagonal': [
                'port',
                'adapter',
                'domain_model',
                'use_case'
            ]
        }

    def validate_inputs(self, project_path: str) -> bool:
        if not Path(project_path).exists():
            logger.error(f"Project path does not exist: {project_path}")
            return False
        return True

    def analyze_code_patterns(self, file_path: Path) -> Dict:
        findings = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            for pattern_type, keywords in self.patterns.items():
                matches = []
                for keyword in keywords:
                    if keyword.lower() in content.lower():
                        matches.append(keyword)
                
                if matches:
                    findings[pattern_type] = matches
            
            if file_path.suffix == '.py':
                try:
                    tree = ast.parse(content)
                    imports = []
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            imports.extend([alias.name for alias in node.names])
                        elif isinstance(node, ast.ImportFrom):
                            imports.append(node.module)
                    
                    findings['imports'] = imports
                except:
                    pass
            
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {str(e)}")
        
        return findings

    def analyze_dependencies(self, project_path: str) -> Dict:
        results = {
            'direct_dependencies': [],
            'transitive_dependencies': [],
            'circular_dependencies': []
        }
        
        try:
            if Path('requirements.txt').exists():
                with open('requirements.txt', 'r') as f:
                    results['direct_dependencies'] = [
                        line.strip() for line in f 
                        if line.strip() and not line.startswith('#')
                    ]
            
            if Path('package.json').exists():
                with open('package.json', 'r') as f:
                    pkg_data = json.load(f)
                    results['direct_dependencies'] = list(
                        pkg_data.get('dependencies', {}).keys()
                    )
        except Exception as e:
            logger.error(f"Error analyzing dependencies: {str(e)}")
        
        return results

    def analyze_coupling(self, project_path: str) -> Dict:
        results = {
            'coupling_score': 0.0,
            'cohesion_score': 0.0,
            'highly_coupled_modules': []
        }
        
        return results

    def detect_pattern(self, project_path: str) -> str:
        """Detect primary architecture pattern"""
        pattern_scores = {pattern: 0 for pattern in self.patterns.keys()}
        
        p = Path(project_path)
        
        for file_path in p.rglob('*'):
            if not file_path.is_file():
                continue
            
            if file_path.suffix not in ['.py', '.js', '.java', '.go', '.ts']:
                continue
            
            findings = self.analyze_code_patterns(file_path)
            
            for pattern in pattern_scores:
                if pattern in findings:
                    pattern_scores[pattern] += 1
        
        primary_pattern = max(pattern_scores, key=pattern_scores.get)
        return primary_pattern

    def analyze(self, project_path: str = '.') -> Dict:
        if not self.validate_inputs(project_path):
            return self.analysis_results

        logger.info(f"Starting architecture analysis on {project_path}")

        primary_pattern = self.detect_pattern(project_path)
        dependencies = self.analyze_dependencies(project_path)
        coupling = self.analyze_coupling(project_path)

        self.analysis_results = {
            'project_path': project_path,
            'primary_pattern': primary_pattern,
            'dependencies': dependencies,
            'coupling_analysis': coupling
        }

        logger.info(f"Architecture analysis completed. Primary pattern: {primary_pattern}")
        return self.analysis_results

    def generate_report(self, output_format: str = 'json') -> str:
        if output_format == 'json':
            return json.dumps(self.analysis_results, indent=2)
        elif output_format == 'text':
            report = []
            report.append(f"Architecture Analysis Report")
            report.append(f"=" * 50)
            report.append(f"Project: {self.analysis_results.get('project_path', 'unknown')}")
            report.append(f"Primary Pattern: {self.analysis_results.get('primary_pattern', 'unknown')}")
            report.append(f"\nDependencies:")
            deps = self.analysis_results.get('dependencies', {})
            report.append(f"  Direct: {len(deps.get('direct_dependencies', []))}")
            report.append(f"  Top 10: {deps.get('direct_dependencies', [])[:10]}")
            return "\n".join(report)
        return json.dumps(self.analysis_results, indent=2)

def main():
    parser = argparse.ArgumentParser(description='Architecture Pattern Analysis')
    parser.add_argument('path', nargs='?', default='.', help='Project path to analyze')
    parser.add_argument('--config', help='Configuration file path (YAML/JSON)')
    parser.add_argument('--format', choices=['json', 'text'], default='json',
                        help='Output format')
    parser.add_argument('--output', help='Output file path')

    args = parser.parse_args()

    analyzer = ArchitectureAnalyzer(args.config)
    results = analyzer.analyze(args.path)
    report = analyzer.generate_report(args.format)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        logger.info(f"Report saved to {args.output}")
    else:
        print(report)

    logger.info("Architecture analysis completed")
    sys.exit(0)

if __name__ == '__main__':
    main()
