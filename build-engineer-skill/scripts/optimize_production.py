#!/usr/bin/env python3
"""
Production Build Optimization
Implements various optimization strategies for production builds
"""

import json
import sys
import argparse
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def generate_optimization_config(output_path: Path):
    webpack_opt = """module.exports = {
  mode: 'production',
  
  optimization: {
    minimize: true,
    minimizer: [
      new TerserPlugin({
        terserOptions: {
          compress: {
            drop_console: true,
            drop_debugger: true,
            pure_funcs: ['console.log', 'console.info', 'console.debug'],
          },
          mangle: {
            safari10: true,
          },
        },
        extractComments: false,
      }),
      new CssMinimizerPlugin({
        minimizerOptions: {
          preset: [
            'default',
            {
              discardComments: { removeAll: true },
              normalizeWhitespace: true,
            },
          ],
        },
      }),
    ],
    
    usedExports: true,
    sideEffects: true,
    concatenateModules: true,
  },
};
"""

    vite_opt = """export default defineConfig({
  build: {
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      },
    },
    
    cssCodeSplit: true,
    cssMinify: true,
    
    chunkSizeWarningLimit: 500,
    
    reportCompressedSize: true,
  },
});
"""

    with open(output_path / 'webpack.optimization.js', 'w') as f:
        f.write(webpack_opt)

    with open(output_path / 'vite.optimization.ts', 'w') as f:
        f.write(vite_opt)

    logger.info("✓ Production optimization configurations generated")


def generate_compression_config(output_path: Path):
    nginx_config = """server {
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript
               application/json application/javascript application/xml+rss
               application/rss+xml font/truetype font/opentype
               application/vnd.ms-fontobject image/svg+xml;

    brotli on;
    brotli_comp_level 6;
    brotli_types text/plain text/css text/xml text/javascript
                  application/json application/javascript application/xml+rss
                  application/rss+xml font/truetype font/opentype
                  application/vnd.ms-fontobject image/svg+xml;
}
"""

    with open(output_path / 'nginx.conf', 'w') as f:
        f.write(nginx_config)

    logger.info("✓ Compression configuration generated")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Optimize production build')
    parser.add_argument('--output', default='.', help='Output directory')
    args = parser.parse_args()

    output_path = Path(args.output)
    generate_optimization_config(output_path)
    generate_compression_config(output_path)
