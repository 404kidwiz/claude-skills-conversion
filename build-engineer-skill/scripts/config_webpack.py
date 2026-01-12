#!/usr/bin/env python3
"""
Webpack Configuration Generator
Supports modern JavaScript/TypeScript applications
"""

import json
import sys
import argparse
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def generate_webpack_config(output_path: Path, config: dict):
    content = f"""const path = require('path');
const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');
const TerserPlugin = require('terser-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');

const isProduction = process.env.NODE_ENV === 'production';
const isDevelopment = !isProduction;

module.exports = {{
  mode: isProduction ? 'production' : 'development',
  
  entry: {{
    main: './src/index.{config.get('language', 'tsx')}',
  }},

  output: {{
    path: path.resolve(__dirname, '{config.get('output_dir', 'dist')}'),
    filename: isProduction ? '[name].[contenthash].js' : '[name].js',
    chunkFilename: isProduction ? '[name].[contenthash].js' : '[name].js',
    clean: true,
    publicPath: '/',
  }},

  resolve: {{
    extensions: ['.ts', '.tsx', '.js', '.jsx', '.json'],
    alias: {{
      '@': path.resolve(__dirname, './src'),
    }},
  }},

  module: {{
    rules: [
      {{
        test: /\\.(ts|tsx)$/,
        use: 'ts-loader',
        exclude: /node_modules/,
      }},
      {{
        test: /\\.(js|jsx)$/,
        exclude: /node_modules/,
        use: {{
          loader: 'babel-loader',
          options: {{
            presets: ['@babel/preset-env', '@babel/preset-react', '@babel/preset-typescript'],
            plugins: [
              '@babel/plugin-transform-runtime',
              '@babel/plugin-proposal-class-properties',
            ],
          }},
        }},
      }},
      {{
        test: /\\.css$/,
        use: [
          isDevelopment ? 'style-loader' : MiniCssExtractPlugin.loader,
          'css-loader',
          'postcss-loader',
        ],
      }},
      {{
        test: /\\.(scss|sass)$/,
        use: [
          isDevelopment ? 'style-loader' : MiniCssExtractPlugin.loader,
          'css-loader',
          'postcss-loader',
          'sass-loader',
        ],
      }},
      {{
        test: /\\.(png|jpe?g|gif|svg|webp)$/,
        type: 'asset',
        parser: {{
          dataUrlCondition: {{
            maxSize: 8 * 1024,
          }},
        }},
        generator: {{
          filename: 'images/[name].[contenthash][ext]',
        }},
      }},
      {{
        test: /\\.(woff|woff2|eot|ttf|otf)$/,
        type: 'asset/resource',
        generator: {{
          filename: 'fonts/[name][ext]',
        }},
      }},
    ],
  }},

  plugins: [
    new CleanWebpackPlugin(),
    
    new HtmlWebpackPlugin({{
      template: './public/index.html',
      filename: 'index.html',
      minify: isProduction,
      inject: true,
    }}),

    ...(isProduction ? [
      new MiniCssExtractPlugin({{
        filename: 'css/[name].[contenthash].css',
        chunkFilename: 'css/[name].[contenthash].css',
      }}),
      
      new BundleAnalyzerPlugin({{
        analyzerMode: 'static',
        openAnalyzer: false,
        generateStatsFile: true,
      }}),
    ] : []),
  ],

  optimization: {{
    minimize: isProduction,
    minimizer: [
      new TerserPlugin({{
        terserOptions: {{
          compress: {{
            drop_console: isProduction,
            drop_debugger: true,
            pure_funcs: isProduction ? ['console.log', 'console.info'] : [],
          }},
        }},
        extractComments: false,
      }}),
      new CssMinimizerPlugin(),
    ],
    
    splitChunks: {{
      chunks: 'all',
      minSize: 20000,
      maxSize: 244000,
      minChunks: 1,
      maxAsyncRequests: 30,
      maxInitialRequests: 30,
      automaticNameDelimiter: '~',
      cacheGroups: {{
        vendors: {{
          test: /[\\\\/]node_modules[\\\\/]/,
          priority: 10,
          reuseExistingChunk: true,
          name: 'vendors',
        }},
        common: {{
          minChunks: 2,
          priority: 5,
          reuseExistingChunk: true,
          name: 'common',
        }},
      }},
    }},
    
    runtimeChunk: 'single',
  }},

  devServer: {{
    static: {{
      directory: path.join(__dirname, 'public'),
    }},
    hot: isDevelopment,
    open: isDevelopment,
    historyApiFallback: true,
    compress: true,
    port: {config.get('port', 3000)},
    client: {{
      overlay: {{
        errors: true,
        warnings: false,
      }},
    }},
  }},

  devtool: isDevelopment ? 'eval-cheap-module-source-map' : 'source-map',

  stats: {{
    colors: true,
    hash: false,
    version: false,
    timings: true,
    assets: true,
    chunks: false,
    modules: false,
  }},
}};
"""

    with open(output_path / 'webpack.config.js', 'w') as f:
        f.write(content)

    logger.info("✓ Webpack configuration generated")


def main():
    parser = argparse.ArgumentParser(description='Generate Webpack configuration')
    parser.add_argument('--output', default='.', help='Output directory')
    parser.add_argument('--language', default='tsx', help='Entry file extension')
    parser.add_argument('--port', type=int, default=3000, help='Dev server port')
    args = parser.parse_args()

    config = {
        'language': args.language,
        'output_dir': 'dist',
        'port': args.port,
    }

    output_path = Path(args.output)
    generate_webpack_config(output_path, config)


if __name__ == '__main__':
    main()
