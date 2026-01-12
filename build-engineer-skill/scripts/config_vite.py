#!/usr/bin/env python3
"""
Vite Configuration Generator
Fast build tool for modern web apps
"""

import json
import sys
import argparse
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def generate_vite_config(output_path: Path, config: dict):
    content = f"""import {{ defineConfig }} from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({{
  plugins: [
    react({{
      jsxImportSource: '{config.get('jsx_runtime', 'react')}',
      babel: {{
        plugins: [
          '@emotion/babel-plugin',
          'babel-plugin-styled-components',
        ],
      }},
    }}),
  ],

  resolve: {{
    alias: {{
      '@': path.resolve(__dirname, './src'),
    }},
  }},

  build: {{
    outDir: '{config.get('output_dir', 'dist')}',
    emptyOutDir: true,
    
    sourcemap: {str(config.get('sourcemap', False)).lower()},
    
    minify: 'terser',
    terserOptions: {{
      compress: {{
        drop_console: {str(config.get('drop_console', True)).lower()},
        drop_debugger: true,
      }},
    }},
    
    rollupOptions: {{
      output: {{
        manualChunks: {{
          vendor: ['react', 'react-dom', 'react-router-dom'],
          ui: ['@mui/material', '@mui/icons-material'],
        }},
      }},
    }},
    
    chunkSizeWarningLimit: {config.get('chunk_size_limit', 1000)},
    
    commonjsOptions: {{
      transformMixedEsModules: true,
    }},
  }},

  server: {{
    port: {config.get('port', 3000)},
    host: true,
    open: {str(config.get('open', True)).lower()},
    cors: true,
    
    proxy: {{
      '/api': {{
        target: '{config.get('api_proxy', 'http://localhost:3000')}',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\\/api/, ''),
      }},
    }},
  }},

  optimizeDeps: {{
    include: ['react', 'react-dom'],
    exclude: [],
  }},

  define: {{
    __APP_VERSION__: JSON.stringify(require('./package.json').version),
  }},
}});
"""

    with open(output_path / 'vite.config.ts', 'w') as f:
        f.write(content)

    logger.info("✓ Vite configuration generated")


def generate_vite_config_react(output_path: Path):
    content = """import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },

  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: (id) => {
          if (id.includes('node_modules')) {
            if (id.includes('react')) return 'react-vendor';
            if (id.includes('ui') || id.includes('material')) return 'ui-vendor';
            return 'vendor';
          }
        },
      },
    },
  },

  server: {
    port: 3000,
    open: true,
    host: true,
  },
});
"""

    with open(output_path / 'vite.config.ts', 'w') as f:
        f.write(content)

    logger.info("✓ Vite React configuration generated")


def main():
    parser = argparse.ArgumentParser(description='Generate Vite configuration')
    parser.add_argument('--output', default='.', help='Output directory')
    parser.add_argument('--port', type=int, default=3000, help='Dev server port')
    parser.add_argument('--framework', default='react', help='Framework')
    args = parser.parse_args()

    config = {
        'output_dir': 'dist',
        'sourcemap': False,
        'drop_console': True,
        'port': args.port,
        'open': True,
        'chunk_size_limit': 1000,
        'jsx_runtime': 'react',
        'api_proxy': 'http://localhost:3000',
    }

    output_path = Path(args.output)
    
    if args.framework == 'react':
        generate_vite_config_react(output_path)
    else:
        generate_vite_config(output_path, config)


if __name__ == '__main__':
    main()
