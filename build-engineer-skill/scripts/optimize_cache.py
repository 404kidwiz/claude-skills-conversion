#!/usr/bin/env python3
"""
Build Cache Optimization Setup
Implements caching strategies for faster builds
"""

import json
import sys
import argparse
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def generate_cache_config(output_path: Path, config: dict):
    webpack_cache = """module.exports = {
  cache: {
    type: 'filesystem',
    cacheDirectory: path.resolve(__dirname, '.webpack_cache'),
    maxAge: 1000 * 60 * 60 * 24 * 7,
    compression: 'gzip',
    buildDependencies: {
      config: [__filename],
    },
  },
};
"""

    vite_cache = """export default {
  optimizeDeps: {
    cacheDir: './node_modules/.vite',
  },
};
"""

    eslint_cache = """module.exports = {
  cache: true,
  cacheLocation: '.eslintcache',
};
"""

    babel_cache = """{
  "cacheDirectory": true,
  "cacheCompression": true
}
"""

    tsconfig_cache = """{
  "compilerOptions": {
    "incremental": true,
    "tsBuildInfoFile": ".tsbuildinfo"
  }
}
"""

    cache_dir = output_path / 'cache_configurations'
    cache_dir.mkdir(parents=True, exist_ok=True)

    with open(cache_dir / 'webpack.cache.js', 'w') as f:
        f.write(webpack_cache)

    with open(cache_dir / 'vite.cache.ts', 'w') as f:
        f.write(vite_cache)

    with open(cache_dir / '.eslintrc.cache.js', 'w') as f:
        f.write(eslint_cache)

    with open(cache_dir / 'babel.cache.json', 'w') as f:
        f.write(babel_cache)

    with open(cache_dir / 'tsconfig.cache.json', 'w') as f:
        f.write(tsconfig_cache)

    gitignore = """# Build cache
.webpack_cache/
.vite/
.eslintcache
.tsbuildinfo
.parcel-cache/
.turbo/
node_modules/
dist/
build/
.out/
"""

    with open(output_path / '.gitignore', 'a') as f:
        f.write('\n' + gitignore)

    logger.info("✓ Cache optimization configurations generated")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Setup build cache optimization')
    parser.add_argument('--output', default='.', help='Output directory')
    args = parser.parse_args()

    config = {'cache_dir': '.webpack_cache'}
    output_path = Path(args.output)
    generate_cache_config(output_path, config)
