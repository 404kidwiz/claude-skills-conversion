#!/usr/bin/env python3
"""
API Documentation Generator (OpenAPI/Swagger)
"""

import sys
import argparse
from pathlib import Path
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def generate_openapi_spec(output_path: Path, config: dict):
    spec = {
        "openapi": "3.0.0",
        "info": {
            "title": config.get("title", "API Documentation"),
            "version": config.get("version", "1.0.0"),
            "description": config.get("description", "API documentation")
        },
        "servers": config.get("servers", [{"url": "http://localhost:8080/api/v1"}]),
        "paths": {},
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                }
            },
            "schemas": {}
        },
        "security": [{"bearerAuth": []}]
    }

    output_path.mkdir(parents=True, exist_ok=True)
    with open(output_path / 'openapi.json', 'w') as f:
        json.dump(spec, f, indent=2)

    logger.info(f"✓ Generated OpenAPI specification")


def main():
    parser = argparse.ArgumentParser(description='Generate API documentation')
    parser.add_argument('--output', default='.', help='Output directory')
    parser.add_argument('--config', help='Config file (JSON)')
    args = parser.parse_args()

    output_path = Path(args.output)

    config = {}
    if args.config:
        try:
            with open(args.config, 'r') as f:
                config = json.load(f)
        except FileNotFoundError:
            logger.error(f"Config file not found: {args.config}")
            sys.exit(1)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in config file: {args.config}")
            sys.exit(1)

    try:
        generate_openapi_spec(output_path, config)
    except Exception as e:
        logger.error(f"Error generating documentation: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
