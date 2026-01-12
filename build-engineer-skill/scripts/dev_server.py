#!/usr/bin/env python3
"""
Development Server Configuration
Setup efficient local development environment
"""

import json
import sys
import argparse
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def generate_vite_dev_server(output_path: Path):
    content = """import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],

  server: {
    host: true,
    port: 3000,
    strictPort: false,
    open: true,
    cors: true,
    
    proxy: {
      '/api': {
        target: 'http://localhost:3000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
    
    hmr: {
      overlay: {
        errors: true,
        warnings: false,
      },
    },
    
    watch: {
      usePolling: false,
      interval: 100,
    },
  },

  preview: {
    port: 4173,
    open: true,
  },
});
"""

    with open(output_path / 'vite.dev.config.ts', 'w') as f:
        f.write(content)

    logger.info("✓ Vite dev server configuration generated")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Setup development server')
    parser.add_argument('--output', default='.', help='Output directory')
    parser.add_argument('--bundler', choices=['vite', 'webpack'], default='vite',
                        help='Bundler type')
    args = parser.parse_args()

    output_path = Path(args.output)
    generate_vite_dev_server(output_path)
